"""Cadastra (ou promove) um tecnico direto no banco, fora da API.

Por seguranca, o /registro publico so cria usuarios comuns. Tecnicos sao
criados por este script, que so quem tem acesso ao servidor/banco consegue rodar.

Uso (na pasta do projeto, com o ambiente virtual ativo):
    python criar_tecnico.py

O banco usado e o da variavel DATABASE_URL (lida do .env pelo app.py).
A senha e digitada na hora e nao aparece na tela nem fica salva no codigo.
"""
from getpass import getpass

from werkzeug.security import generate_password_hash

from app import app
from models import db, Usuario
# Mesmas regras da API, para o script nao aceitar o que o /registro recusaria
from validacoes import TAMANHO_MINIMO_SENHA, email_valido


def criar_tecnico(nome, email, senha):
    """Cria um tecnico novo ou promove a tecnico um usuario que ja existe.

    Devolve "criado" ou "promovido", para quem chamou saber o que aconteceu.
    Fica separada do input() para poder ser testada com pytest.
    """
    usuario = Usuario.query.filter_by(email=email).first()

    if usuario:
        # Ja existe alguem com esse email: so troca o papel e a senha
        usuario.papel = "tecnico"
        usuario.senha_hash = generate_password_hash(senha)
        resultado = "promovido"
    else:
        usuario = Usuario(
            nome=nome,
            email=email,
            senha_hash=generate_password_hash(senha),  # nunca salvamos a senha pura
            papel="tecnico"
        )
        db.session.add(usuario)
        resultado = "criado"

    db.session.commit()
    return resultado


def main():
    """Parte interativa: pergunta os dados no terminal."""
    print("=== Cadastro de tecnico ===")
    nome = input("Nome: ").strip()
    email = input("Email: ").strip().lower()

    # getpass le a senha sem mostrar o que esta sendo digitado
    senha = getpass("Senha: ")
    confirmacao = getpass("Confirme a senha: ")

    if not nome or not email:
        print("Erro: nome e email sao obrigatorios.")
        return
    if not email_valido(email):
        print("Erro: email invalido.")
        return
    if senha != confirmacao:
        print("Erro: as senhas nao conferem.")
        return
    if len(senha) < TAMANHO_MINIMO_SENHA:
        print(f"Erro: a senha precisa ter pelo menos {TAMANHO_MINIMO_SENHA} caracteres.")
        return

    # O app_context da acesso ao banco configurado no Flask
    with app.app_context():
        resultado = criar_tecnico(nome, email, senha)

    print(f"Tecnico {resultado} com sucesso: {email}")


# So roda o main() quando o arquivo e executado direto (python criar_tecnico.py),
# e nao quando ele e importado (como nos testes)
if __name__ == "__main__":
    main()
