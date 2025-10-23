# 💬 HPro Chat

Um sistema de chat em tempo real com múltiplas salas e mensagens privadas, desenvolvido com Flask e inspirado no tema VS Code Dark.

## ✨ Funcionalidades

### 🔐 Autenticação

- Sistema completo de registro e login
- Senhas criptografadas com SHA256
- Gerenciamento de sessões
- Sistema de IDs internos para usuários

### 💬 Chat em Tempo Real

- **Múltiplas salas públicas**: Geral, Dev, Random, Suporte
- **Salas ocultas**: Secret e VIP (acesso apenas por URL)
- **Mensagens privadas**: Duplo clique no username para abrir chat privado em nova aba
- **Indicador de digitação**: Mostra quando outros usuários estão digitando
- **Animações**: Efeito de brilho em mensagens novas
- **Notificações**: Som e pisca na aba do navegador para novas mensagens
- **Histórico**: Todas as mensagens são persistidas em arquivos JSON

### 🎨 Interface

- **Tema VS Code Dark**: Interface estilo editor de código
- **Sidebar colapsível**: Minimizada por padrão, expande com hover
- **Sistema de abas**: Alterne entre sala pública e chats privados
- **Design responsivo**: Otimizado para desktop e mobile (incluindo iPhone)
- **Scrollbar customizada**: Visual consistente com o tema

### ⚡ Otimizações

- Polling inteligente (2s para mensagens, 3s para indicador de digitação)
- Otimizado para uso com ngrok (limite de 360 req/min)
- Cache eficiente de mensagens

## 🚀 Instalação

### Pré-requisitos

- Python 3.7+
- Flask

### Passos

1. Clone o repositório:

```bash
git clone <seu-repositorio>
cd chat
```

2. Instale as dependências:

```bash
pip install flask
```

3. Execute o servidor:

```bash
python app.py
```

4. Acesse no navegador:

```
http://localhost:5000
```

## 🌐 Configuração com ngrok

Para acessar o chat de qualquer lugar:

1. Instale o [ngrok](https://ngrok.com/)

2. Execute o servidor Flask:

```bash
python app.py
```

3. Em outro terminal, inicie o ngrok:

```bash
ngrok http 5000
```

4. Compartilhe a URL gerada (ex: `https://xyz.ngrok-free.app`)

## 📁 Estrutura do Projeto

```
chat/
├── app.py                 # Backend Flask
├── rooms.json            # Configuração das salas
├── migrate_users.py      # Script de migração de dados
├── data/                 # Dados persistidos
│   ├── users.json       # Usuários e senhas
│   ├── chat_*.json      # Histórico de mensagens por sala
│   └── private_*.json   # Mensagens privadas
└── templates/
    ├── index.html       # Interface do chat
    └── login.html       # Página de login/registro
```

## 🎮 Como Usar

### Primeiro Acesso

1. Crie uma conta na página de registro
2. Faça login com suas credenciais

### Chat Público

1. Use a sidebar para navegar entre salas
2. Digite mensagens e pressione Enter ou clique em "Enviar"
3. Veja quem está digitando em tempo real

### Mensagens Privadas

1. Dê duplo clique no username de qualquer usuário
2. Uma nova aba será aberta com o chat privado
3. Alterne entre abas para gerenciar múltiplas conversas
4. Feche abas clicando no "×" (exceto a sala principal)

### Salas Ocultas

- Acesse diretamente pela URL:
  - `/secret` - Sala Secreta 🔒
  - `/vip` - Sala VIP ⭐

## ⚙️ Configuração

### Adicionar Novas Salas

Edite o arquivo `rooms.json`:

```json
{
  "rooms": [
    {
      "id": "nova-sala",
      "name": "Nova Sala",
      "icon": "🎯",
      "hidden": false
    }
  ]
}
```

### Alterar Chave Secreta

Em `app.py`, modifique a linha:

```python
app.secret_key = 'sua_chave_secreta_aqui_mude_isso_em_producao'
```

## 🔒 Segurança

- ✅ Senhas criptografadas com SHA256
- ✅ Validação de sessão em todas as rotas protegidas
- ✅ Proteção contra acesso não autorizado
- ⚠️ **IMPORTANTE**: Altere a `secret_key` em produção
- ⚠️ **IMPORTANTE**: Use HTTPS em produção (ngrok fornece automaticamente)

## 🎨 Personalização

### Cores do Tema

As cores principais estão definidas no CSS em `templates/index.html`:

- Background: `#1e1e1e`
- Texto: `#d4d4d4`
- Accent: `#007acc`
- Hover: `#2d2d2d`

### Sons de Notificação

O som de notificação pode ser alterado modificando a URL em:

```html
<audio id="notificationSound" preload="auto">
  <source src="URL_DO_SEU_AUDIO" type="audio/mp3" />
</audio>
```

## 🐛 Resolução de Problemas

### Mensagens não aparecem

- Verifique se está autenticado
- Limpe o cache do navegador
- Recarregue a página (F5)

### Erro 401 (Não autenticado)

- Faça logout e login novamente
- Limpe o localStorage do navegador
- Verifique se a sessão não expirou

### Chat privado não abre

- Certifique-se de dar duplo clique no username
- Não tente abrir chat consigo mesmo
- Verifique se está em uma sala pública primeiro

## 📝 Migração de Dados

Se você tem uma versão antiga do sistema de usuários, execute:

```bash
python migrate_users.py
```

Isso converterá a estrutura antiga para o formato com IDs internos.

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📜 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🎯 Roadmap

- [ ] WebSocket para comunicação em tempo real (substituir polling)
- [ ] Upload de imagens e arquivos
- [ ] Emojis e reações
- [ ] Menções (@usuario)
- [ ] Markdown nas mensagens
- [ ] Histórico de mensagens paginado
- [ ] Admin panel
- [ ] Ban/kick de usuários
- [ ] Roles e permissões
- [ ] Temas personalizáveis

## 👨‍💻 Autor

Desenvolvido com ❤️ para comunicação em equipe

## 🙏 Agradecimentos

- Flask por ser um framework incrível
- VS Code pelo tema inspirador
- Comunidade open source

---

**Nota**: Este é um projeto educacional. Para uso em produção, considere adicionar:

- Banco de dados (PostgreSQL, MySQL)
- WebSocket (Socket.IO)
- Rate limiting mais robusto
- Logs estruturados
- Testes automatizados
- CI/CD
