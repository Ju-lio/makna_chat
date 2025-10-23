# Sistema de Salas de Chat

## Como funciona

O sistema agora suporta múltiplas salas de chat! Cada sala tem seu próprio histórico de mensagens e pode ser acessada por uma URL específica.

## Salas disponíveis

As salas são configuradas no arquivo `rooms.json`. Atualmente temos:

- **Sala Geral** (`/`) - 💬 Chat principal
- **Sala de Desenvolvimento** (`/dev`) - 👨‍💻 Discussões sobre código
- **Sala Random** (`/random`) - 🎲 Assuntos aleatórios
- **Sala de Suporte** (`/suporte`) - 🆘 Ajuda técnica

## Como adicionar uma nova sala

1. Abra o arquivo `rooms.json`
2. Adicione um novo objeto ao array `rooms`:

```json
{
  "id": "nome-da-sala",
  "name": "Nome Exibido",
  "url": "/nome-da-sala",
  "description": "Descrição da sala",
  "icon": "🎨"
}
```

3. Salve o arquivo
4. Reinicie o servidor Flask
5. Um novo arquivo `data/chat_nome-da-sala.json` será criado automaticamente

## Estrutura de uma sala

```json
{
  "id": "id-unico", // Identificador único (sem espaços)
  "name": "Nome da Sala", // Nome exibido na interface
  "url": "/rota", // URL de acesso
  "description": "Descrição", // Descrição da sala
  "icon": "🚀" // Emoji/ícone da sala
}
```

## Exemplo: Adicionando uma sala de Games

Edite `rooms.json` e adicione:

```json
{
  "id": "games",
  "name": "Sala de Games",
  "url": "/games",
  "description": "Discussões sobre jogos e gaming",
  "icon": "🎮"
}
```

Pronto! A sala estará disponível em: `http://localhost:5000/games`

## Arquivos criados automaticamente

Para cada sala, o sistema cria automaticamente:

- `data/chat_{id}.json` - Arquivo com o histórico de mensagens da sala

## Salas Ocultas 🔒

Você pode criar salas que **não aparecem na sidebar**, mas são acessíveis pela URL direta!

### Como criar uma sala oculta:

Adicione `"hidden": true` na configuração da sala:

```json
{
  "id": "secret",
  "name": "Sala Secreta",
  "url": "/secret",
  "description": "Sala oculta - Acesso apenas por URL",
  "icon": "🔒",
  "hidden": true
}
```

### Características das salas ocultas:

- ✅ **Não aparecem** na lista de salas da sidebar
- ✅ **Acessíveis apenas pela URL** direta
- ✅ Mostram um badge **"🔒 Oculta"** no título da aba
- ✅ Funcionam exatamente como salas normais
- ✅ Perfeitas para salas privadas, VIP, ou exclusivas

### Exemplos de uso:

- Salas de moderação
- Salas VIP para membros especiais
- Salas de teste
- Salas temporárias
- Salas temáticas secretas

## URLs com ngrok

Se estiver usando ngrok, as salas funcionam da mesma forma:

- `https://seu-url.ngrok-free.dev/`
- `https://seu-url.ngrok-free.dev/dev`
- `https://seu-url.ngrok-free.dev/games`
- `https://seu-url.ngrok-free.dev/secret` _(sala oculta)_
- etc.
