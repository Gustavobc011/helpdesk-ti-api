import pytest

DADOS_VALIDOS = {
    "nome": "Maria Silva",
    "email": "maria@empresa.com",
    "senha": "123456"
}


# parametrize roda o mesmo teste uma vez para cada linha da lista.
# Cada linha e (corpo enviado, trecho esperado na mensagem de erro).
@pytest.mark.parametrize("corpo, trecho_erro", [
    ({"email": "maria@empresa.com", "senha": "123456"}, "'nome' e obrigatorio"),
    ({"nome": "Maria", "senha": "123456"}, "'email' e obrigatorio"),
    ({"nome": "Maria", "email": "maria@empresa.com"}, "'senha' e obrigatorio"),
    ({**DADOS_VALIDOS, "nome": "   "}, "'nome' e obrigatorio"),
    ({**DADOS_VALIDOS, "email": "maria-sem-arroba"}, "e-mail valido"),
    ({**DADOS_VALIDOS, "email": "maria@empresa"}, "e-mail valido"),
    ({**DADOS_VALIDOS, "senha": "123"}, "pelo menos 6"),
    ({**DADOS_VALIDOS, "nome": "x" * 101}, "no maximo 100"),
    ({**DADOS_VALIDOS, "nome": 123}, "deve ser um texto"),
])
def test_registro_com_dados_invalidos(client, corpo, trecho_erro):
    """Cada tipo de dado invalido deve ser recusado com 400 e uma mensagem clara."""
    resposta = client.post("/registro", json=corpo)

    assert resposta.status_code == 400
    detalhes = resposta.get_json()["detalhes"]
    assert any(trecho_erro in mensagem for mensagem in detalhes)


def test_registro_mostra_todos_os_erros_juntos(client):
    """Com varios problemas, a resposta deve listar todos de uma vez."""
    resposta = client.post("/registro", json={})

    assert resposta.status_code == 400
    assert len(resposta.get_json()["detalhes"]) == 3


def test_registro_sem_json(client):
    """Corpo que nao e JSON deve dar 400, e nao erro 500."""
    resposta = client.post("/registro", data="isso nao e json", content_type="text/plain")

    assert resposta.status_code == 400


def test_email_e_padronizado_em_minusculo(client):
    """Cadastrar com maiusculas e logar com minusculas deve funcionar."""
    client.post("/registro", json={**DADOS_VALIDOS, "email": "  Maria@Empresa.COM "})

    resposta = client.post("/login", json={"email": "maria@empresa.com", "senha": "123456"})
    assert resposta.status_code == 200

    # E o mesmo e-mail com outra capitalizacao conta como duplicado
    duplicado = client.post("/registro", json={**DADOS_VALIDOS, "email": "MARIA@empresa.com"})
    assert duplicado.status_code == 409


@pytest.mark.parametrize("corpo", [
    {},
    {"email": "maria@empresa.com"},
    {"senha": "123456"},
])
def test_login_sem_campos_obrigatorios(client, corpo):
    """Login sem email ou senha deve dar 400, e nao erro 500."""
    resposta = client.post("/login", json=corpo)

    assert resposta.status_code == 400
