"""Script para migrar usuários do formato antigo para o novo formato com IDs."""
import json

OLD_FORMAT_FILE = 'data/users.json'
BACKUP_FILE = 'data/users_backup.json'

def migrate_users():
    """Converte formato antigo {username: {data}} para novo formato com IDs."""
    
    # Carrega usuários no formato antigo
    try:
        with open(OLD_FORMAT_FILE, 'r', encoding='utf-8') as f:
            old_users = json.load(f)
    except FileNotFoundError:
        print("Arquivo users.json não encontrado. Nada a migrar.")
        return
    
    # Verifica se já está no formato novo
    if 'users' in old_users and 'next_id' in old_users:
        print("Arquivo já está no formato novo. Nada a fazer.")
        return
    
    # Faz backup
    with open(BACKUP_FILE, 'w', encoding='utf-8') as f:
        json.dump(old_users, f, indent=4, ensure_ascii=False)
    print(f"✓ Backup criado em {BACKUP_FILE}")
    
    # Converte para novo formato
    new_users_data = {
        'users': [],
        'next_id': 1
    }
    
    for username, data in old_users.items():
        new_user = {
            'id': new_users_data['next_id'],
            'username': username,
            'password': data['password'],
            'created_at': data['created_at']
        }
        new_users_data['users'].append(new_user)
        new_users_data['next_id'] += 1
        print(f"✓ Migrado: {username} (ID: {new_user['id']})")
    
    # Salva no novo formato
    with open(OLD_FORMAT_FILE, 'w', encoding='utf-8') as f:
        json.dump(new_users_data, f, indent=4, ensure_ascii=False)
    
    print(f"\n✅ Migração concluída!")
    print(f"   Total de usuários migrados: {len(new_users_data['users'])}")
    print(f"   Próximo ID: {new_users_data['next_id']}")

if __name__ == '__main__':
    migrate_users()
