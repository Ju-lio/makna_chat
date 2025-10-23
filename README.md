# Chat local

Um chat em tempo real com interface estilo IDE, desenvolvido com Flask e JavaScript puro. Possui chat público e privado, com suporte a notificações e design responsivo.

## 🚀 Funcionalidades

### Chat Principal

- Interface estilo IDE com tema escuro
- Atualizações em tempo real
- Sistema de login simples
- Codificação de mensagens em base64
- Design responsivo para mobile

### Chat Privado (/rato)

- Rota privada para conversas reservadas
- Som de notificação para novas mensagens
- Título piscante quando minimizado
- Mesma interface do chat principal
- Codificação independente das mensagens

## 🛠️ Tecnologias Utilizadas

- **Backend**: Python/Flask
- **Frontend**: HTML5, CSS3, JavaScript
- **Armazenamento**: Memória (lista Python)
- **Autenticação**: LocalStorage
- **Estilo**: IDE-like dark theme

## 📦 Instalação

1. Clone o repositório:

```bash
git clone [url-do-repositorio]
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

- Chat principal: `http://localhost:5000`
- Chat privado: `http://localhost:5000/rato`

## 💻 Como Usar

1. Acesse a aplicação no navegador
2. Digite seu nome de usuário na tela de login
3. Você será redirecionado para o chat principal
4. Para chat privado, acesse a rota `/rato`

## 📱 Recursos Mobile

- Interface adaptativa
- Botões e inputs otimizados para toque
- Layout simplificado em telas pequenas
- Suporte a orientação retrato e paisagem

## 🔐 Segurança

- Codificação base64 para todas as mensagens
- Rotas separadas para chat público e privado
- Verificação de login em todas as páginas

## 🌟 Features Especiais

1. **Notificações**:

   - Som ao receber mensagens
   - Título piscante quando minimizado
   - Volume ajustável do som

2. **Interface**:

   - Tema escuro estilo IDE
   - Barra de status
   - Números de linha nas mensagens
   - Scrollbar estilizado

3. **UX**:
   - Enter para enviar mensagens
   - Auto-scroll para novas mensagens
   - Indicadores de status

## 📝 Notas de Desenvolvimento

- Projeto desenvolvido com foco em simplicidade
- Sem dependências externas além do Flask
- Código limpo e bem documentado
- Pronto para expansões futuras

## 🔄 Updates Futuros Planejados

- [ ] Persistência de dados
- [ ] Salas de chat customizadas
- [ ] Sistema de menções
- [ ] Emojis e formatação de texto
- [ ] Lista de usuários online
