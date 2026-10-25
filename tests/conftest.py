import os

# Estas variaveis precisam ser definidas ANTES de importar o app,
# para ele usar o banco de teste e nao o banco real
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["JWT_SECRET_KEY"] = "chave-de-teste-com-mais-de-32-caracteres-ok"

import pytest
from werkzeug.security import generate_password_hash
from app import app as flask_app
from models import db, Usuario


@pytest.fixture
def client():
    """Entrega um cliente de teste com banco limpo para cada teste."""
    with flask_app.app_context():
        db.create_all()
        yield flask_app.test_client()
        db.session.remove()
        db.drop_all()



SENHA_TESTE = "123456"


def _logar(client, email):
    """Faz login e devolve o cabecalho de autorizacao com o token."""
    resposta = client.post("/login", json={"email": email, "senha": SENHA_TESTE})
    token = resposta.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _criar_e_logar(client, nome, email):
    """Cadastra um usuario comum pela API (/registro) e faz login."""
    client.post("/registro", json={
        "nome": nome,
        "email": email,
        "senha": SENHA_TESTE
    })
    return _logar(client, email)


@pytest.fixture
def headers_usuario(client):
    """Cabecalho de autorizacao de um usuario comum."""
    return _criar_e_logar(client, "Usuario", "usuario@teste.com")


@pytest.fixture
def headers_outro_usuario(client):
    """Cabecalho de autorizacao de um segundo usuario comum."""
    return _criar_e_logar(client, "Outro Usuario", "outro@teste.com")


@pytest.fixture
def headers_tecnico(client):
    """Cabecalho de autorizacao de um tecnico.

    O /registro nao cria mais tecnicos (correcao de seguranca), entao o
    tecnico e inserido direto no banco, do mesmo jeito que o script
    criar_tecnico.py faz em producao.
    """
    tecnico = Usuario(
        nome="Tecnico",
        email="tecnico@teste.com",
        senha_hash=generate_password_hash(SENHA_TESTE),
        papel="tecnico"
    )
    db.session.add(tecnico)
    db.session.commit()
    return _logar(client, "tecnico@teste.com")