# LinkedIn Bot

Automatize a criação e publicação de posts no LinkedIn a partir de artigos de tecnologia. Este projeto:

1. Coleta artigos de RSS feeds (temas configuráveis).
2. Gera sugestões de texto para LinkedIn usando OpenAI.
3. Permite aprovação e edição via CLI.
4. Publica no LinkedIn usando um token manual (`token.json`).

---

## Pré-requisitos

- **Python 3.8+**  
- **Virtualenv** (recomendado)  
- Conta de **LinkedIn Developer** com um App criado  
- Chave válida **OPENAI_API_KEY**  

---

## 🚀 Instalação

```bash
# Clone o repositório
git clone https://github.com/jefferson-up/LinkedIn-Bot.git
cd linkedin-bot

# Crie e ative o ambiente virtual
python -m venv venv
# macOS / Linux
source venv/bin/activate
# Windows
venv\Scripts\activate

# Instale dependências
pip install -r requirements.txt
```

---

## Configuração de Ambiente

Copie o `.env.example` para `.env` e preencha:

```env
OPENAI_API_KEY="sua_chave_openai"
LINKEDIN_CLIENT_ID="seu_client_id"
LINKEDIN_CLIENT_SECRET="seu_client_secret"
```

---

## Gerando o Token de Acesso LinkedIn manualmente

Em vez de implementar o fluxo 3‑legged OAuth, utilize a ferramenta **OAuth 2.0 Helper** do LinkedIn Developer Portal:

1. Acesse o [LinkedIn Developer Portal](https://www.linkedin.com/developers).
2. Selecione seu App.
3. Navegue até **Tools → OAuth 2.0 Helper**.
4. Marque as permissões `r_liteprofile` e `w_member_social`.
5. Clique em **Generate access token**.
6. Copie o JSON de resposta e salve num arquivo `token.json` na raiz do projeto.

O `token.json` ficará no formato:

```json
{
  "access_token": "AQX...",
  "expires_in": 5184000,
  "scope": "r_liteprofile w_member_social"
}
```

---

## Uso

### 1. Coletar e aprovar posts via CLI

```bash
# Executa o CLI de aprovação
python src/cli.py -o approved.json
```

1. Ele exibirá até 3 artigos (temas aleatórios).
2. Para cada artigo, exibe 3 sugestões geradas.
3. Ao final, um JSON com `{ link, theme, text }` será impresso.

### 2. Publicar no LinkedIn

```bash
python src/poster.py approved.json
```

* `approved.json` é o arquivo de saída do CLI.
* O `poster.py` usa `token.json` para autenticar e publica cada post no seu perfil.

---

## Configuração de Temas

Ajuste `config/themes.yaml` para:

* Definir seu perfil (`profile`).
* Quantidade de artigos e variações.
* Temas, feeds RSS, palavras-chave e templates.

---

## Estrutura do Projeto

```text
linkedin-bot/
├── .env.example        # modelo de variáveis de ambiente
├── token.json          # seu token OAuth 2.0 manual
├── history.json        # links já processados (auto gerado)
├── approved.json       # saída do CLI de aprovação
├── requirements.txt    # dependências Python
├── config/
│   └── themes.yaml     # perfil, temas e RSS feeds
└── src/
    ├── auth.py         # carrega token de token.json
    ├── fetcher.py      # coleta artigos dos RSS feeds
    ├── generator.py    # gera sugestões de post com OpenAI
    ├── cli.py          # CLI interativo de aprovação
    └── poster.py       # publica no LinkedIn via API

```
---

## Contribuições

Pull requests são bem-vindos! Sinta-se à vontade para sugerir novos temas, melhorar prompts ou fluxos de autenticação.

---

## Licença

MIT © Jefferson Barbosa
