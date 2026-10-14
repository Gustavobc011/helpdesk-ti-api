# Helpdesk TI API

API REST para um sistema de chamados de suporte de TI, com autenticação JWT
e dois perfis de acesso: usuário e técnico/admin.

## Tecnologias

Python, Flask, SQLAlchemy, Flask-JWT-Extended, Flasgger (Swagger), pytest, Docker, gunicorn

## Funcionalidades

- Cadastro e login de usuários com senha criptografada e token JWT
- Usuário comum abre chamados e acompanha apenas os seus
- Técnico/admin vê todos os chamados e atualiza o status
- Comentários nos chamados (visíveis ao dono e ao técnico)
- Endpoint de métricas: total de chamados por status, prioridade e categoria
- Documentação interativa com Swagger
- Testes automatizados com pytest

## Como rodar localmente

```bash
git clone https://github.com/Gustavobc011/helpdesk-ti-api.git
cd helpdesk-ti-api
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Crie um arquivo `.env` na raiz com uma chave secreta:

```
JWT_SECRET_KEY=sua-chave-com-mais-de-32-caracteres
```

Inicie o servidor:

```bash
python app.py
```

A documentação fica em http://127.0.0.1:5000/apidocs

## Como rodar com Docker

```bash
docker build -t helpdesk-api .
docker run --rm -p 5000:5000 --env-file .env helpdesk-api
```

## Testes

```bash
pytest -v
```

## Principais endpoints

| Método | Rota | Acesso |
|--------|------|--------|
| POST | /registro | Público |
| POST | /login | Público |
| POST | /chamados | Autenticado |
| GET | /chamados | Autenticado (só os seus) |
| GET | /chamados/todos | Técnico/admin |
| PATCH | /chamados/{id}/status | Técnico/admin |
| POST/GET | /chamados/{id}/comentarios | Dono ou técnico |
| GET | /metricas | Técnico/admin |

## Autor

Gustavo, estudante de Análise e Desenvolvimento de Sistemas.
GitHub: https://github.com/Gustavobc011