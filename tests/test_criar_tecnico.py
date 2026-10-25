from criar_tecnico import criar_tecnico


def test_script_cria_tecnico_que_consegue_logar(client):
    """O script deve criar um tecnico novo, e o login deve devolver papel "tecnico"."""
    resultado = criar_tecnico("Ana Tecnica", "ana@empresa.com", "senha-forte")
    assert resultado == "criado"

    login = client.post("/login", json={"email": "ana@empresa.com", "senha": "senha-forte"})
    assert login.status_code == 200
    assert login.get_json()["papel"] == "tecnico"


def test_script_promove_usuario_existente(client):
    """Se o email ja for de um usuario comum, o script deve promove-lo a tecnico."""
    client.post("/registro", json={
        "nome": "Joao",
        "email": "joao@empresa.com",
        "senha": "123456"
    })

    resultado = criar_tecnico("Joao", "joao@empresa.com", "nova-senha")
    assert resultado == "promovido"

    login = client.post("/login", json={"email": "joao@empresa.com", "senha": "nova-senha"})
    assert login.get_json()["papel"] == "tecnico"
