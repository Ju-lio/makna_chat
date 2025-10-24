from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_from_directory
from datetime import datetime
import socket
import json
import os
import hashlib
import base64
import uuid

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui_mude_isso_em_producao'  # Necessário para sessions

# Garante que os diretórios necessários existem
os.makedirs('data', exist_ok=True)
os.makedirs('data/uploads', exist_ok=True)

# Configurações de upload
UPLOAD_FOLDER = 'data/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# Arquivo de usuários e galeria
USERS_FILE = 'data/users.json'
GALLERY_FILE = 'data/gallery.json'

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

def load_gallery():
    """Carrega galeria de memes do arquivo JSON."""
    try:
        with open(GALLERY_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('memes', [])
    except FileNotFoundError:
        return []

def save_gallery(memes):
    """Salva galeria de memes no arquivo JSON."""
    with open(GALLERY_FILE, 'w', encoding='utf-8') as f:
        json.dump({'memes': memes}, f, indent=4, ensure_ascii=False)

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

def allowed_file(filename):
    """Verifica se a extensão do arquivo é permitida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload-image', methods=['POST'])
def upload_image():
    """Endpoint para upload de imagens (paste ou arquivo)."""
    if 'username' not in session:
        return jsonify({'status': 'error', 'message': 'Não autenticado'}), 401
    
    try:
        # Verifica se é paste (base64) ou upload de arquivo
        if 'image_data' in request.json:
            # Paste de clipboard (base64)
            image_data = request.json['image_data']
            room_id = request.json.get('room_id', 'geral')
            is_private_msg = request.json.get('is_private', False)
            target_user = request.json.get('target_user', None)
            tags = request.json.get('tags', '')  # Tags do meme
            is_private_gallery = request.json.get('is_private_gallery', False)  # Private na galeria
            
            # Remove o prefixo data:image/...;base64,
            if 'base64,' in image_data:
                image_data = image_data.split('base64,')[1]
            
            # Decodifica e salva
            image_bytes = base64.b64decode(image_data)
            
            # Gera nome único
            filename = f"{uuid.uuid4()}.png"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            
            with open(filepath, 'wb') as f:
                f.write(image_bytes)
            
            # Adiciona à galeria
            gallery = load_gallery()
            meme_entry = {
                'filename': filename,
                'uploaded_by': session['username'],
                'uploaded_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'tags': [tag.strip().lower() for tag in tags.split(',') if tag.strip()],
                'is_private': is_private_gallery,
                'room_id': room_id if not is_private_msg else None,
                'target_user': target_user if is_private_msg else None
            }
            gallery.append(meme_entry)
            save_gallery(gallery)
            
            # Cria mensagem com imagem
            message = {
                'user': session['username'],
                'message': f'[IMAGE:{filename}]',
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'type': 'image'
            }
            
            # Salva mensagem
            if is_private_msg and target_user:
                # Mensagem privada
                current_user = session['username']
                users_sorted = sorted([current_user.lower(), target_user.lower()])
                conversation_id = f"{users_sorted[0]}_{users_sorted[1]}"
                conv_file = f'data/private_{conversation_id}.json'
                
                if os.path.exists(conv_file):
                    with open(conv_file, 'r', encoding='utf-8') as f:
                        messages = json.load(f)
                else:
                    messages = []
                
                message['from'] = current_user
                message['to'] = target_user
                message['date'] = datetime.now().strftime('%Y-%m-%d')
                messages.append(message)
                
                with open(conv_file, 'w', encoding='utf-8') as f:
                    json.dump(messages, f, indent=4, ensure_ascii=False)
            else:
                # Mensagem pública
                if room_id not in room_messages:
                    room_messages[room_id] = []
                
                room_messages[room_id].append(message)
                save_messages(room_messages[room_id], f'chat_{room_id}.json')
            
            return jsonify({'status': 'success', 'filename': filename})
        else:
            return jsonify({'status': 'error', 'message': 'Nenhuma imagem fornecida'}), 400
            
    except Exception as e:
        print(f"Erro ao fazer upload de imagem: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve arquivos de upload."""
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/gallery', methods=['GET'])
def get_gallery():
    """Retorna memes da galeria filtrados por tags e privacidade."""
    if 'username' not in session:
        return jsonify({'status': 'error', 'message': 'Não autenticado'}), 401
    
    search_tags = request.args.get('tags', '').lower().strip()
    current_user = session['username']
    room_id = request.args.get('room_id', 'geral')
    is_private_chat = request.args.get('is_private', 'false') == 'true'
    target_user = request.args.get('target_user', '')
    
    gallery = load_gallery()
    filtered_memes = []
    
    for meme in gallery:
        # Verifica privacidade
        if meme.get('is_private', False):
            # Meme privado - só mostra se foi upado pelo usuário atual ou na conversa atual
            if meme.get('uploaded_by') != current_user:
                # Se não foi upado pelo user, verifica se está na conversa privada correta
                if is_private_chat:
                    meme_target = meme.get('target_user', '')
                    if not (meme_target == target_user or meme_target == current_user):
                        continue
                else:
                    continue
        
        # Filtra por tags se fornecido
        if search_tags:
            search_list = [tag.strip() for tag in search_tags.split(',') if tag.strip()]
            meme_tags = meme.get('tags', [])
            
            # Verifica se alguma tag bate
            if not any(search_tag in meme_tags for search_tag in search_list):
                continue
        
        filtered_memes.append(meme)
    
    return jsonify({'status': 'success', 'memes': filtered_memes})

@app.route('/sewage')
def sewage():
    """Rota para o player de vídeos do YouTube."""
    return render_template('sewage.html')

if __name__ == '__main__':
    local_ip = get_local_ip()
    print(f"\nServidor rodando em: http://{local_ip}:5000")
    print("Compartilhe este endereço com seu colega para começar a conversar!\n")
    app.run(host='0.0.0.0', port=5000, debug=True)