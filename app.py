from flask import Flask, render_template, request, jsonify
from datetime import datetime
import socket
import json
import os

app = Flask(__name__)

# Garante que o diretório de dados existe
os.makedirs('data', exist_ok=True)

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
    return render_template('login.html', rooms=rooms)

@app.route('/')
def home():
    """Rota principal que renderiza a interface do chat - Sala Geral."""
    room = next((r for r in rooms if r['id'] == 'geral'), rooms[0] if rooms else None)
    return render_template('index.html', room=room, rooms=rooms)

# Cria rotas dinâmicas para cada sala
@app.route('/<room_id>')
def room_chat(room_id):
    """Rota dinâmica para cada sala de chat."""
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

@app.route('/messages')
def get_messages():
    """Retorna todas as mensagens de uma sala específica."""
    try:
        room_id = request.args.get('room_id', 'geral')
        if room_id not in room_messages:
            room_messages[room_id] = []
        return jsonify(room_messages[room_id])
    except Exception as e:
        print(f"Erro ao buscar mensagens: {e}")
        return jsonify([])

@app.route('/rato')
def private_chat():
    """Rota para o chat privado."""
    return render_template('private.html')

@app.route('/send-private', methods=['POST'])
def send_private():
    """Endpoint para enviar mensagens privadas."""
    try:
        data = request.get_json()
        message = {
            'user': data['user'],
            'message': data['message'],
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }
        private_messages.append(message)
        save_messages(private_messages, 'private_messages.json')
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Erro ao enviar mensagem privada: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/messages-private')
def get_private_messages():
    """Retorna todas as mensagens do chat privado."""
    try:
        return jsonify(private_messages)
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