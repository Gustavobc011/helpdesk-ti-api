def test_home(client):
    """A rota inicial deve responder 200 com uma mensagem."""
    resposta = client.get("/")

    assert resposta.status_code == 200
    assert "mensagem" in resposta.get_json()