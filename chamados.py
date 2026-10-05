from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Chamado, Usuario, Comentario

chamados_bp = Blueprint("chamados", __name__)


@chamados_bp.route("/chamados", methods=["POST"])
@jwt_required()
def criar_chamado():
    """Cria um novo chamado, associado ao usuario autenticado pelo token."""
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
    """Lista apenas os chamados abertos pelo usuario autenticado."""
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


@chamados_bp.route("/chamados/todos", methods=["GET"])
@jwt_required()
def listar_todos_chamados():
    """Lista todos os chamados do sistema. Acesso restrito a tecnico/admin."""
    usuario_id = get_jwt_identity()
    usuario = Usuario.query.get(usuario_id)

    # Checagem de autorizacao: so passa quem tem papel de tecnico ou admin
    if usuario.papel not in ["tecnico", "admin"]:
        return jsonify({"erro": "Acesso restrito a tecnicos e administradores"}), 403

    chamados = Chamado.query.all()

    resultado = []
    for chamado in chamados:
        resultado.append({
            "id": chamado.id,
            "titulo": chamado.titulo,
            "descricao": chamado.descricao,
            "categoria": chamado.categoria,
            "prioridade": chamado.prioridade,
            "status": chamado.status,
            "usuario_id": chamado.usuario_id
        })

    return jsonify(resultado), 200


@chamados_bp.route("/chamados/<int:chamado_id>/status", methods=["PATCH"])
@jwt_required()
def atualizar_status(chamado_id):
    """Atualiza o status de um chamado. Acesso restrito a tecnico/admin."""
    usuario_id = get_jwt_identity()
    usuario = Usuario.query.get(usuario_id)

    if usuario.papel not in ["tecnico", "admin"]:
        return jsonify({"erro": "Acesso restrito a tecnicos e administradores"}), 403

    chamado = Chamado.query.get(chamado_id)

    if not chamado:
        return jsonify({"erro": "Chamado nao encontrado"}), 404

    dados = request.get_json()
    novo_status = dados.get("status")

    status_validos = ["aberto", "em andamento", "resolvido"]
    if novo_status not in status_validos:
        return jsonify({"erro": f"Status invalido. Use um de: {status_validos}"}), 400

    chamado.status = novo_status
    chamado.tecnico_id = usuario_id
    db.session.commit()

    return jsonify({"mensagem": "Status atualizado com sucesso", "status": chamado.status}), 200


def usuario_pode_acessar_chamado(usuario, chamado):
    """Retorna True se o usuario for tecnico/admin ou o dono do chamado."""
    eh_equipe = usuario.papel in ["tecnico", "admin"]
    eh_dono = chamado.usuario_id == usuario.id
    return eh_equipe or eh_dono


@chamados_bp.route("/chamados/<int:chamado_id>/comentarios", methods=["POST"])
@jwt_required()
def adicionar_comentario(chamado_id):
    """Adiciona um comentario a um chamado (dono do chamado ou tecnico/admin)."""
    usuario = Usuario.query.get(get_jwt_identity())
    chamado = Chamado.query.get(chamado_id)

    if not chamado:
        return jsonify({"erro": "Chamado nao encontrado"}), 404

    if not usuario_pode_acessar_chamado(usuario, chamado):
        return jsonify({"erro": "Voce nao tem acesso a este chamado"}), 403

    dados = request.get_json()

    novo_comentario = Comentario(
        texto=dados["texto"],
        chamado_id=chamado.id,
        usuario_id=usuario.id
    )

    db.session.add(novo_comentario)
    db.session.commit()

    return jsonify({"mensagem": "Comentario adicionado com sucesso", "id": novo_comentario.id}), 201


@chamados_bp.route("/chamados/<int:chamado_id>/comentarios", methods=["GET"])
@jwt_required()
def listar_comentarios(chamado_id):
    """Lista os comentarios de um chamado, do mais antigo ao mais recente."""
    usuario = Usuario.query.get(get_jwt_identity())
    chamado = Chamado.query.get(chamado_id)

    if not chamado:
        return jsonify({"erro": "Chamado nao encontrado"}), 404

    if not usuario_pode_acessar_chamado(usuario, chamado):
        return jsonify({"erro": "Voce nao tem acesso a este chamado"}), 403

    comentarios = Comentario.query.filter_by(chamado_id=chamado.id).order_by(Comentario.data_criacao).all()

    resultado = []
    for comentario in comentarios:
        resultado.append({
            "id": comentario.id,
            "texto": comentario.texto,
            "usuario_id": comentario.usuario_id,
            "data_criacao": comentario.data_criacao.isoformat()
        })

    return jsonify(resultado), 200