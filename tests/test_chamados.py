DADOS_CHAMADO = {
    "titulo": "Computador nao liga",
    "descricao": "A maquina nao sai do modo de espera",
    "categoria": "hardware"
}


def test_criar_chamado(client, headers_usuario):
    """Usuario autenticado consegue criar um chamado."""
    resposta = client.post("/chamados", json=DADOS_CHAMADO, headers=headers_usuario)

    assert resposta.status_code == 201
    assert "id" in resposta.get_json()


def test_criar_chamado_sem_token(client):
    """Sem token, a criacao de chamado deve ser recusada com 401."""
    resposta = client.post("/chamados", json=DADOS_CHAMADO)

    assert resposta.status_code == 401


def test_usuario_ve_apenas_seus_chamados(client, headers_usuario, headers_outro_usuario):
    """Um usuario nao enxerga os chamados de outro usuario."""
    client.post("/chamados", json=DADOS_CHAMADO, headers=headers_usuario)

    resposta = client.get("/chamados", headers=headers_outro_usuario)

    assert resposta.status_code == 200
    assert resposta.get_json() == []


def test_usuario_comum_nao_lista_todos(client, headers_usuario):
    """Usuario comum nao pode acessar a lista geral de chamados."""
    resposta = client.get("/chamados/todos", headers=headers_usuario)

    assert resposta.status_code == 403


def test_tecnico_lista_todos(client, headers_usuario, headers_tecnico):
    """Tecnico enxerga os chamados de todos os usuarios."""
    client.post("/chamados", json=DADOS_CHAMADO, headers=headers_usuario)

    resposta = client.get("/chamados/todos", headers=headers_tecnico)

    assert resposta.status_code == 200
    assert len(resposta.get_json()) == 1


def test_tecnico_atualiza_status(client, headers_usuario, headers_tecnico):
    """Tecnico consegue mudar o status de um chamado."""
    criado = client.post("/chamados", json=DADOS_CHAMADO, headers=headers_usuario)
    chamado_id = criado.get_json()["id"]

    resposta = client.patch(
        f"/chamados/{chamado_id}/status",
        json={"status": "em andamento"},
        headers=headers_tecnico
    )

    assert resposta.status_code == 200
    assert resposta.get_json()["status"] == "em andamento"


def test_usuario_comum_nao_atualiza_status(client, headers_usuario):
    """Usuario comum nao pode mudar o status, nem do proprio chamado."""
    criado = client.post("/chamados", json=DADOS_CHAMADO, headers=headers_usuario)
    chamado_id = criado.get_json()["id"]

    resposta = client.patch(
        f"/chamados/{chamado_id}/status",
        json={"status": "resolvido"},
        headers=headers_usuario
    )

    assert resposta.status_code == 403


def test_status_invalido_e_recusado(client, headers_usuario, headers_tecnico):
    """Status fora da lista permitida deve devolver 400."""
    criado = client.post("/chamados", json=DADOS_CHAMADO, headers=headers_usuario)
    chamado_id = criado.get_json()["id"]

    resposta = client.patch(
        f"/chamados/{chamado_id}/status",
        json={"status": "banana"},
        headers=headers_tecnico
    )

    assert resposta.status_code == 400