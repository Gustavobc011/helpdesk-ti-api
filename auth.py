from flask import Blueprint, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from models import db, Usuario
from validacoes import ler_json, validar_texto, validar_email, validar_senha, resposta_de_erro

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/registro", methods=["POST"])
def registro():
    """Cadastra um novo usuario.
    ---
    tags:
      - Autenticacao
    parameters:
      - in: body
        name: corpo
        required: true
        schema:
          type: object
          required:
            - nome
            - email
            - senha
          properties:
            nome:
              type: string
              example: Maria Silva
            email:
              type: string
              example: maria@empresa.com
            senha:
              type: string
              example: "123456"
    responses:
      201:
        description: Usuario cadastrado com sucesso (sempre com papel "usuario")
      400:
        description: Dados invalidos (campo faltando, e-mail invalido ou senha curta)
      409:
        description: Email ja cadastrado
    """
    dados = ler_json()

    # Valida tudo de uma vez, para o cliente ver todos os problemas juntos.
    # Os tamanhos maximos sao os mesmos das colunas em models.py.
    erro = resposta_de_erro(
        validar_texto(dados, "nome", maximo=100),
        validar_email(dados),
        validar_senha(dados),
    )
    if erro:
        return erro

    # Padroniza o e-mail (sem espacos e minusculo) para "Maria@x.com" e
    # "maria@x.com" serem tratados como o mesmo e-mail
    nome = dados["nome"].strip()
    email = dados["email"].strip().lower()

    usuario_existente = Usuario.query.filter_by(email=email).first()
    if usuario_existente:
        return jsonify({"erro": "Email ja cadastrado"}), 409

    senha_hash = generate_password_hash(dados["senha"])

    # SEGURANCA: o papel NUNCA vem do corpo da requisicao.
    # Se viesse, qualquer pessoa poderia mandar {"papel": "tecnico"} e ganhar
    # permissoes de tecnico. O registro publico sempre cria um "usuario" comum;
    # tecnicos sao cadastrados pelo script criar_tecnico.py, fora da API.
    novo_usuario = Usuario(
        nome=nome,
        email=email,
        senha_hash=senha_hash,
        papel="usuario"
    )

    db.session.add(novo_usuario)
    db.session.commit()

    return jsonify({"mensagem": "Usuario cadastrado com sucesso"}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """Autentica o usuario e devolve o token de acesso.
    ---
    tags:
      - Autenticacao
    parameters:
      - in: body
        name: corpo
        required: true
        schema:
          type: object
          required:
            - email
            - senha
          properties:
            email:
              type: string
              example: maria@empresa.com
            senha:
              type: string
              example: "123456"
    responses:
      200:
        description: Login realizado, devolve access_token e papel
      400:
        description: Email ou senha nao enviados
      401:
        description: Email ou senha invalidos
    """
    dados = ler_json()

    # No login so checamos se os campos vieram. Regras de formato/tamanho
    # ficam no cadastro; aqui um dado errado simplesmente nao vai bater (401).
    erro = resposta_de_erro(
        validar_texto(dados, "email"),
        validar_texto(dados, "senha"),
    )
    if erro:
        return erro

    email = dados["email"].strip().lower()
    usuario = Usuario.query.filter_by(email=email).first()

    if not usuario or not check_password_hash(usuario.senha_hash, dados["senha"]):
        return jsonify({"erro": "Email ou senha invalidos"}), 401

    token = create_access_token(identity=str(usuario.id))

    return jsonify({"access_token": token, "papel": usuario.papel}), 200