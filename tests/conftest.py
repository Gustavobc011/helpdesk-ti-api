import os

# Estas variaveis precisam ser definidas ANTES de importar o app,
# para ele usar o banco de teste e nao o banco real
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["JWT_SECRET_KEY"] = "chave-de-teste-com-mais-de-32-caracteres-ok"

import pytest
from app import app as flask_app
from models import db


@pytest.fixture
def client():
    """Entrega um cliente de teste com banco limpo para cada teste."""
    with flask_app.app_context():
        db.create_all()
        yield flask_app.test_client()
        db.session.remove()
        db.drop_all()



def _criar_e_logar(client, nome, email, papel="usuario"):
    """Cadastra um usuario, faz login e devolve o cabecalho de autorizacao."""
    client.post("/registro", json={
        "nome": nome,
        "email": email,
        "senha": "123456",
        "papel": papel
    })
    resposta = client.post("/login", json={"email": email, "senha": "123456"})
    token = resposta.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


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
    """Cabecalho de autorizacao de um tecnico."""
    return _criar_e_logar(client, "Tecnico", "tecnico@teste.com", papel="tecnico")