from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from models import db, Usuario

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/registro", methods=["POST"])
def registro():
    dados = request.get_json()

    usuario_existente = Usuario.query.filter_by(email=dados["email"]).first()
    if usuario_existente:
        return jsonify({"erro": "Email ja cadastrado"}), 409

    senha_hash = generate_password_hash(dados["senha"])

    novo_usuario = Usuario(
        nome=dados["nome"],
        email=dados["email"],
        senha_hash=senha_hash,
        papel=dados.get("papel", "usuario")
    )

    db.session.add(novo_usuario)
    db.session.commit()

    return jsonify({"mensagem": "Usuario cadastrado com sucesso"}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    dados = request.get_json()

    usuario = Usuario.query.filter_by(email=dados["email"]).first()

    if not usuario or not check_password_hash(usuario.senha_hash, dados["senha"]):
        return jsonify({"erro": "Email ou senha invalidos"}), 401

    token = create_access_token(identity=str(usuario.id))

    return jsonify({"access_token": token, "papel": usuario.papel}), 200