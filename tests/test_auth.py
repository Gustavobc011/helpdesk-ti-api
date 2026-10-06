# Dados reaproveitados em varios testes, para nao repetir
DADOS_USUARIO = {
    "nome": "Usuario Teste",
    "email": "usuario@teste.com",
    "senha": "123456"
}


def test_registro_com_sucesso(client):
    """Cadastrar um usuario novo deve devolver 201 (criado)."""
    resposta = client.post("/registro", json=DADOS_USUARIO)

    assert resposta.status_code == 201


def test_registro_email_duplicado(client):
    """Cadastrar o mesmo email duas vezes deve devolver 409 (conflito)."""
    client.post("/registro", json=DADOS_USUARIO)
    resposta = client.post("/registro", json=DADOS_USUARIO)

    assert resposta.status_code == 409


def test_login_com_sucesso(client):
    """Login com email e senha corretos deve devolver o token e o papel."""
    client.post("/registro", json=DADOS_USUARIO)

    resposta = client.post("/login", json={
        "email": DADOS_USUARIO["email"],
        "senha": DADOS_USUARIO["senha"]
    })

    assert resposta.status_code == 200
    assert "access_token" in resposta.get_json()
    assert resposta.get_json()["papel"] == "usuario"


def test_login_com_senha_errada(client):
    """Login com senha incorreta deve devolver 401 (nao autorizado)."""
    client.post("/registro", json=DADOS_USUARIO)

    resposta = client.post("/login", json={
        "email": DADOS_USUARIO["email"],
        "senha": "senha-errada"
    })

    assert resposta.status_code == 401