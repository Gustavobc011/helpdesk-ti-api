import pytest

DADOS_CHAMADO = {
    "titulo": "Computador nao liga",
    "descricao": "A maquina nao sai do modo de espera",
    "categoria": "hardware"
}


@pytest.mark.parametrize("corpo, trecho_erro", [
    ({"descricao": "x", "categoria": "hardware"}, "'titulo' e obrigatorio"),
    ({"titulo": "x", "categoria": "hardware"}, "'descricao' e obrigatorio"),
    ({"titulo": "x", "descricao": "x"}, "'categoria' e obrigatorio"),
    ({**DADOS_CHAMADO, "titulo": "x" * 151}, "no maximo 150"),
    ({**DADOS_CHAMADO, "categoria": "x" * 51}, "no maximo 50"),
    ({**DADOS_CHAMADO, "prioridade": "urgentissima"}, "'prioridade' deve ser um de"),
])
def test_criar_chamado_com_dados_invalidos(client, headers_usuario, corpo, trecho_erro):
    """Chamado com campo faltando, grande demais ou prioridade invalida da 400."""
    resposta = client.post("/chamados", json=corpo, headers=headers_usuario)

    assert resposta.status_code == 400
    assert any(trecho_erro in m for m in resposta.get_json()["detalhes"])


def test_criar_chamado_com_prioridade_valida(client, headers_usuario):
    """Uma prioridade da lista deve ser aceita e salva."""
    client.post("/chamados", json={**DADOS_CHAMADO, "prioridade": "critica"}, headers=headers_usuario)

    chamados = client.get("/chamados", headers=headers_usuario).get_json()
    assert chamados[0]["prioridade"] == "critica"


def test_atualizar_status_sem_corpo(client, headers_usuario, headers_tecnico):
    """PATCH de status sem corpo JSON deve dar 400, e nao erro 500."""
    criado = client.post("/chamados", json=DADOS_CHAMADO, headers=headers_usuario)
    chamado_id = criado.get_json()["id"]

    resposta = client.patch(f"/chamados/{chamado_id}/status", headers=headers_tecnico)

    assert resposta.status_code == 400


def test_comentario_vazio_e_recusado(client, headers_usuario):
    """Comentario sem texto (ou so com espacos) deve dar 400."""
    criado = client.post("/chamados", json=DADOS_CHAMADO, headers=headers_usuario)
    chamado_id = criado.get_json()["id"]

    resposta = client.post(
        f"/chamados/{chamado_id}/comentarios",
        json={"texto": "   "},
        headers=headers_usuario
    )

    assert resposta.status_code == 400
