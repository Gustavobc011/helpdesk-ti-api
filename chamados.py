from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Chamado

chamados_bp = Blueprint("chamados", __name__)

@chamados_bp.route("/chamados", methods=["POST"])
@jwt_required()
def criar_chamado():
    usuario_id = get_jwt_identity()
    dados = request.get_json()

    novo_chamado = Chamado(
        titulo=dados["titulo"],
        descricao=dados["descricao"],
        categoria=dados["categoria"],
        prioridade=dados.get("prioridade", "media"),
        usuario_id=usuario_id
    )

    db.session.add(novo_chamado)
    db.session.commit()

    return jsonify({"mensagem": "Chamado criado com sucesso", "id": novo_chamado.id}), 201


@chamados_bp.route("/chamados", methods=["GET"])
@jwt_required()
def listar_meus_chamados():
    usuario_id = get_jwt_identity()
    chamados = Chamado.query.filter_by(usuario_id=usuario_id).all()

    resultado = []
    for chamado in chamados:
        resultado.append({
            "id": chamado.id,
            "titulo": chamado.titulo,
            "descricao": chamado.descricao,
            "categoria": chamado.categoria,
            "prioridade": chamado.prioridade,
            "status": chamado.status
        })

    return jsonify(resultado), 200