from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from models import db, Usuario

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
      409:
        description: Email ja cadastrado
    """
    dados = request.get_json()

    usuario_existente = Usuario.query.filter_by(email=dados["email"]).first()
    if usuario_existente:
        return jsonify({"erro": "Email ja cadastrado"}), 409

    senha_hash = generate_password_hash(dados["senha"])

    # SEGURANCA: o papel NUNCA vem do corpo da requisicao.
    # Se viesse, qualquer pessoa poderia mandar {"papel": "tecnico"} e ganhar
    # permissoes de tecnico. O registro publico sempre cria um "usuario" comum;
    # tecnicos sao cadastrados pelo script criar_tecnico.py, fora da API.
    novo_usuario = Usuario(
        nome=dados["nome"],
        email=dados["email"],
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
      401:
        description: Email ou senha invalidos
    """
    dados = request.get_json()

    usuario = Usuario.query.filter_by(email=dados["email"]).first()

    if not usuario or not check_password_hash(usuario.senha_hash, dados["senha"]):
        return jsonify({"erro": "Email ou senha invalidos"}), 401

    token = create_access_token(identity=str(usuario.id))

    return jsonify({"access_token": token, "papel": usuario.papel}), 200