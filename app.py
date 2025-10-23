from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime
import socket
import json
import os
import hashlib

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui_mude_isso_em_producao'  # Necessário para sessions

# Garante que o diretório de dados existe
os.makedirs('data', exist_ok=True)

# Arquivo de usuários
USERS_FILE = 'data/users.json'

def load_users():
    """Carrega usuários do arquivo JSON.
    Retorna dict com estrutura: {
        'users': [
            {'id': 1, 'username': 'user1', 'password': 'hash', 'created_at': '...'},
            ...
        ],
        'next_id': 2
    }
    """
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Garante que tem a estrutura correta
            if 'users' not in data:
                data = {'users': [], 'next_id': 1}
            return data
    except FileNotFoundError:
        return {'users': [], 'next_id': 1}

def save_users(users_data):
    """Salva usuários no arquivo JSON."""
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users_data, f, indent=4, ensure_ascii=False)

def find_user_by_username(users_data, username):
    """Busca um usuário pelo username."""
    for user in users_data['users']:
        if user['username'].lower() == username.lower():
            return user
    return None

def hash_password(password):
    """Cria hash da senha usando SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()

def load_rooms():
    """Carrega configuração das salas do arquivo JSON."""
    try:
        with open('rooms.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('rooms', [])
    except FileNotFoundError:
        return []

def load_messages(filename):
    """Carrega mensagens do arquivo JSON."""
    try:
        with open(f'data/{filename}', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('messages', [])
    except FileNotFoundError:
        return []

def save_messages(messages, filename):
    """Salva mensagens no arquivo JSON."""
    with open(f'data/{filename}', 'w', encoding='utf-8') as f:
        json.dump({'messages': messages}, f, indent=4, ensure_ascii=False)

# Carrega as salas disponíveis
rooms = load_rooms()

# Dicionário para armazenar mensagens de cada sala em memória
room_messages = {}
for room in rooms:
    room_id = room['id']
    room_messages[room_id] = load_messages(f'chat_{room_id}.json')

# Carrega mensagens privadas
private_messages = load_messages('private_messages.json')

def get_local_ip():
    """Obtém o IP local da máquina para facilitar o acesso em rede."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

@app.route('/login')
def login():
    """Rota para a página de login."""
    # Se já está logado, redireciona para o chat
    if 'username' in session:
        return redirect(url_for('home'))
    return render_template('login.html', rooms=rooms)

@app.route('/logout')
def logout():
    """Rota para fazer logout."""
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['POST'])
def register():
    """Endpoint para registrar novo usuário."""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if not username or not password:
            return jsonify({'success': False, 'message': 'Usuário e senha são obrigatórios'}), 400
        
        if len(username) < 3:
            return jsonify({'success': False, 'message': 'Usuário deve ter no mínimo 3 caracteres'}), 400
        
        if len(password) < 4:
            return jsonify({'success': False, 'message': 'Senha deve ter no mínimo 4 caracteres'}), 400
        
        users_data = load_users()
        
        # Verifica se o username já existe
        if find_user_by_username(users_data, username):
            return jsonify({'success': False, 'message': 'Usuário já existe'}), 400
        
        # Cria novo usuário com ID único
        new_user = {
            'id': users_data['next_id'],
            'username': username,
            'password': hash_password(password),
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        users_data['users'].append(new_user)
        users_data['next_id'] += 1
        
        save_users(users_data)
        
        return jsonify({'success': True, 'message': 'Usuário criado com sucesso!'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao registrar: {str(e)}'}), 500

@app.route('/authenticate', methods=['POST'])
def authenticate():
    """Endpoint para autenticar usuário."""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if not username or not password:
            return jsonify({'success': False, 'message': 'Usuário e senha são obrigatórios'}), 400
        
        users_data = load_users()
        
        # Busca o usuário pelo username
        user = find_user_by_username(users_data, username)
        
        if not user:
            return jsonify({'success': False, 'message': 'Usuário não encontrado'}), 401
        
        if user['password'] != hash_password(password):
            return jsonify({'success': False, 'message': 'Senha incorreta'}), 401
        
        # Salva o username na sessão (mantém compatibilidade com o resto do código)
        session['username'] = user['username']
        session['user_id'] = user['id']
        
        return jsonify({'success': True, 'message': 'Login realizado com sucesso!'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao autenticar: {str(e)}'}), 500

@app.route('/')
def home():
    """Rota principal que renderiza a interface do chat - Sala Geral."""
    # Verifica se o usuário está autenticado
    if 'username' not in session:
        return redirect(url_for('login'))
    
    room = next((r for r in rooms if r['id'] == 'geral'), rooms[0] if rooms else None)
    return render_template('index.html', room=room, rooms=rooms)

# Cria rotas dinâmicas para cada sala
@app.route('/<room_id>')
def room_chat(room_id):
    """Rota dinâmica para cada sala de chat."""
    # Verifica se o usuário está autenticado
    if 'username' not in session:
        return redirect(url_for('login'))
    
    room = next((r for r in rooms if r['id'] == room_id), None)
    if room:
        return render_template('index.html', room=room, rooms=rooms)
    return "Sala não encontrada", 404

@app.route('/send', methods=['POST'])
def send():
    """Endpoint para enviar mensagens.
    
    Espera um JSON com:
    - user: nome do usuário
    - message: conteúdo da mensagem
    - room_id: ID da sala (opcional, padrão: 'geral')
    """
    # Verifica autenticação
    if 'username' not in session:
        return jsonify({'status': 'error', 'message': 'Não autenticado'}), 401
    
    try:
        data = request.get_json()
        room_id = data.get('room_id', 'geral')
        
        message = {
            'user': data['user'],
            'message': data['message'],
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }
        
        # Garante que a sala existe no dicionário
        if room_id not in room_messages:
            room_messages[room_id] = []
        
        room_messages[room_id].append(message)
        save_messages(room_messages[room_id], f'chat_{room_id}.json')
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Dicionário para controlar quem está digitando em cada sala
typing_users = {}

@app.route('/messages')
def get_messages():
    """Retorna todas as mensagens de uma sala específica."""
    # Verifica autenticação
    if 'username' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    try:
        room_id = request.args.get('room_id', 'geral')
        if room_id not in room_messages:
            room_messages[room_id] = []
        return jsonify(room_messages[room_id])
    except Exception as e:
        print(f"Erro ao buscar mensagens: {e}")
        return jsonify([])

@app.route('/typing', methods=['POST'])
def set_typing():
    """Notifica que um usuário está digitando."""
    # Verifica autenticação
    if 'username' not in session:
        return jsonify({'status': 'error', 'message': 'Não autenticado'}), 401
    
    try:
        data = request.get_json()
        user = data.get('user')
        room_id = data.get('room_id', 'geral')
        is_typing = data.get('is_typing', False)
        
        if room_id not in typing_users:
            typing_users[room_id] = {}
        
        if is_typing:
            typing_users[room_id][user] = datetime.now()
        else:
            typing_users[room_id].pop(user, None)
        
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Erro ao atualizar status de digitação: {e}")
        return jsonify({'status': 'error'}), 500

@app.route('/typing')
def get_typing():
    """Retorna lista de usuários que estão digitando."""
    # Verifica autenticação
    if 'username' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    try:
        room_id = request.args.get('room_id', 'geral')
        current_user = request.args.get('user', '')
        
        if room_id not in typing_users:
            return jsonify([])
        
        # Remove usuários que pararam de digitar há mais de 3 segundos
        now = datetime.now()
        active_users = []
        
        for user, last_typing in list(typing_users[room_id].items()):
            if (now - last_typing).seconds < 3:
                if user != current_user:  # Não inclui o próprio usuário
                    active_users.append(user)
            else:
                typing_users[room_id].pop(user, None)
        
        return jsonify(active_users)
    except Exception as e:
        print(f"Erro ao buscar usuários digitando: {e}")
        return jsonify([])

@app.route('/rato')
def private_chat():
    """Rota para o chat privado."""
    return render_template('private.html')

@app.route('/send-private', methods=['POST'])
def send_private():
    """Endpoint para enviar mensagens privadas entre usuários."""
    # Verifica autenticação
    if 'username' not in session:
        return jsonify({'status': 'error', 'message': 'Não autenticado'}), 401
    
    try:
        data = request.get_json()
        from_user = session['username']
        to_user = data['to_user']
        message_text = data['message']
        
        # Cria ID único da conversa (sempre na mesma ordem alfabética)
        users_sorted = sorted([from_user.lower(), to_user.lower()])
        conversation_id = f"{users_sorted[0]}_{users_sorted[1]}"
        
        # Carrega mensagens da conversa
        conv_file = f'data/private_{conversation_id}.json'
        if os.path.exists(conv_file):
            with open(conv_file, 'r', encoding='utf-8') as f:
                messages = json.load(f)
        else:
            messages = []
        
        # Adiciona nova mensagem
        message = {
            'from': from_user,
            'to': to_user,
            'message': message_text,
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'date': datetime.now().strftime('%Y-%m-%d')
        }
        messages.append(message)
        
        # Salva mensagens
        with open(conv_file, 'w', encoding='utf-8') as f:
            json.dump(messages, f, indent=4, ensure_ascii=False)
        
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Erro ao enviar mensagem privada: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/messages-private/<target_user>')
def get_private_messages(target_user):
    """Retorna mensagens privadas entre o usuário atual e outro usuário."""
    # Verifica autenticação
    if 'username' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    try:
        current_user = session['username']
        
        # Cria ID único da conversa
        users_sorted = sorted([current_user.lower(), target_user.lower()])
        conversation_id = f"{users_sorted[0]}_{users_sorted[1]}"
        
        # Carrega mensagens
        conv_file = f'data/private_{conversation_id}.json'
        if os.path.exists(conv_file):
            with open(conv_file, 'r', encoding='utf-8') as f:
                messages = json.load(f)
            return jsonify(messages)
        else:
            return jsonify([])
    except Exception as e:
        print(f"Erro ao buscar mensagens privadas: {e}")
        return jsonify([])

@app.route('/sewage')
def sewage():
    """Rota para o player de vídeos do YouTube."""
    return render_template('sewage.html')

if __name__ == '__main__':
    local_ip = get_local_ip()
    print(f"\nServidor rodando em: http://{local_ip}:5000")
    print("Compartilhe este endereço com seu colega para começar a conversar!\n")
    app.run(host='0.0.0.0', port=5000, debug=True)