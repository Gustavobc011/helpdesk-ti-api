import pytest


@pytest.fixture
def chamado_id(client, headers_usuario):
    """Cria um chamado do usuario comum e devolve o id dele."""
    resposta = client.post("/chamados", json={
        "titulo": "Computador nao liga",
        "descricao": "A maquina nao sai do modo de espera",
        "categoria": "hardware"
    }, headers=headers_usuario)
    return resposta.get_json()["id"]


def test_dono_comenta_no_proprio_chamado(client, chamado_id, headers_usuario):
    """O dono do chamado pode adicionar comentarios."""
    resposta = client.post(
        f"/chamados/{chamado_id}/comentarios",
        json={"texto": "Ja tentei reiniciar"},
        headers=headers_usuario
    )

    assert resposta.status_code == 201


def test_tecnico_comenta_em_qualquer_chamado(client, chamado_id, headers_tecnico):
    """Tecnico pode comentar em chamado de qualquer usuario."""
    resposta = client.post(
        f"/chamados/{chamado_id}/comentarios",
        json={"texto": "Vou verificar amanha"},
        headers=headers_tecnico
    )

    assert resposta.status_code == 201


def test_outro_usuario_nao_comenta(client, chamado_id, headers_outro_usuario):
    """Usuario que nao e dono nem tecnico recebe 403 ao comentar."""
    resposta = client.post(
        f"/chamados/{chamado_id}/comentarios",
        json={"texto": "Posso comentar?"},
        headers=headers_outro_usuario
    )

    assert resposta.status_code == 403


def test_comentar_em_chamado_inexistente(client, headers_usuario):
    """Comentar em um chamado que nao existe devolve 404."""
    resposta = client.post(
        "/chamados/999/comentarios",
        json={"texto": "Alguem ai?"},
        headers=headers_usuario
    )

    assert resposta.status_code == 404


def test_comentar_sem_token(client, chamado_id):
    """Sem token, nao e possivel comentar."""
    resposta = client.post(
        f"/chamados/{chamado_id}/comentarios",
        json={"texto": "Anonimo"}
    )

    assert resposta.status_code == 401


def test_listar_comentarios_em_ordem(client, chamado_id, headers_usuario, headers_tecnico):
    """Os comentarios voltam na ordem em que foram criados."""
    url = f"/chamados/{chamado_id}/comentarios"
    client.post(url, json={"texto": "Primeiro"}, headers=headers_usuario)
    client.post(url, json={"texto": "Segundo"}, headers=headers_tecnico)

    resposta = client.get(url, headers=headers_usuario)
    comentarios = resposta.get_json()

    assert resposta.status_code == 200
    assert len(comentarios) == 2
    assert comentarios[0]["texto"] == "Primeiro"
    assert comentarios[1]["texto"] == "Segundo"


def test_outro_usuario_nao_lista_comentarios(client, chamado_id, headers_outro_usuario):
    """Usuario que nao e dono nem tecnico nao ve os comentarios do chamado."""
    resposta = client.get(
        f"/chamados/{chamado_id}/comentarios",
        headers=headers_outro_usuario
    )

    assert resposta.status_code == 403