DADOS_CHAMADO = {
    "titulo": "Computador nao liga",
    "descricao": "A maquina nao sai do modo de espera",
    "categoria": "hardware"
}


def test_metricas_sem_chamados(client, headers_tecnico):
    """Com o banco vazio, o total e zero e os agrupamentos vem vazios."""
    resposta = client.get("/metricas", headers=headers_tecnico)
    metricas = resposta.get_json()

    assert resposta.status_code == 200
    assert metricas["total"] == 0
    assert metricas["por_status"] == {}


def test_tecnico_ve_metricas(client, headers_usuario, headers_tecnico):
    """O tecnico recebe os totais agrupados corretamente."""
    client.post("/chamados", json=DADOS_CHAMADO, headers=headers_usuario)
    client.post("/chamados", json={**DADOS_CHAMADO, "prioridade": "alta"}, headers=headers_usuario)

    resposta = client.get("/metricas", headers=headers_tecnico)
    metricas = resposta.get_json()

    assert resposta.status_code == 200
    assert metricas["total"] == 2
    assert metricas["por_status"] == {"aberto": 2}
    assert metricas["por_prioridade"] == {"media": 1, "alta": 1}
    assert metricas["por_categoria"] == {"hardware": 2}


def test_usuario_comum_nao_ve_metricas(client, headers_usuario):
    """Usuario comum recebe 403 ao tentar ver as metricas."""
    resposta = client.get("/metricas", headers=headers_usuario)

    assert resposta.status_code == 403


def test_metricas_sem_token(client):
    """Sem token, a rota de metricas devolve 401."""
    resposta = client.get("/metricas")

    assert resposta.status_code == 401