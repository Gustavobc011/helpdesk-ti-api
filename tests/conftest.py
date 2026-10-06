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