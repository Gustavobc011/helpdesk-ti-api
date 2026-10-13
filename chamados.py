from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Chamado, Usuario, Comentario
from sqlalchemy import func

chamados_bp = Blueprint("chamados", __name__)


@chamados_bp.route("/chamados", methods=["POST"])
@jwt_required()
def criar_chamado():
    """Cria um novo chamado para o usuario autenticado.
    ---
    tags:
      - Chamados
    security:
      - Bearer: []
    parameters:
      - in: body
        name: corpo
        required: true
        schema:
          type: object
          required:
            - titulo
            - descricao
            - categoria
          properties:
            titulo:
              type: string
              example: Computador nao liga
            descricao:
              type: string
              example: A maquina nao sai do modo de espera
            categoria:
              type: string
              example: hardware
            prioridade:
              type: string
              description: Opcional. Padrao "media".
              example: media
    responses:
      201:
        description: Chamado criado com sucesso
      401:
        description: Token ausente ou invalido
    """
        
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
    """Lista os chamados do usuario autenticado.
    ---
    tags:
      - Chamados
    security:
      - Bearer: []
    responses:
      200:
        description: Lista dos chamados do proprio usuario
      401:
        description: Token ausente ou invalido
    """
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
    """Lista todos os chamados do sistema (somente tecnico ou admin).
    ---
    tags:
      - Chamados
    security:
      - Bearer: []
    responses:
      200:
        description: Lista de todos os chamados
      401:
        description: Token ausente ou invalido
      403:
        description: Acesso restrito a tecnicos e administradores
    """
    usuario_id = get_jwt_identity()
    usuario = db.session.get(Usuario, usuario_id)

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
    """Atualiza o status de um chamado (somente tecnico ou admin).
    ---
    tags:
      - Chamados
    security:
      - Bearer: []
    parameters:
      - in: path
        name: chamado_id
        type: integer
        required: true
        description: Id do chamado
      - in: body
        name: corpo
        required: true
        schema:
          type: object
          required:
            - status
          properties:
            status:
              type: string
              enum:
                - aberto
                - em andamento
                - resolvido
              example: em andamento
    responses:
      200:
        description: Status atualizado com sucesso
      400:
        description: Status invalido
      401:
        description: Token ausente ou invalido
      403:
        description: Acesso restrito a tecnicos e administradores
      404:
        description: Chamado nao encontrado
    """
    usuario_id = get_jwt_identity()
    usuario = db.session.get(Usuario, usuario_id)

    if usuario.papel not in ["tecnico", "admin"]:
        return jsonify({"erro": "Acesso restrito a tecnicos e administradores"}), 403

    chamado = db.session.get(Chamado, chamado_id)

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
    """Adiciona um comentario a um chamado (dono do chamado ou tecnico/admin).
    ---
    tags:
      - Comentarios
    security:
      - Bearer: []
    parameters:
      - in: path
        name: chamado_id
        type: integer
        required: true
        description: Id do chamado
      - in: body
        name: corpo
        required: true
        schema:
          type: object
          required:
            - texto
          properties:
            texto:
              type: string
              example: Ja tentei reiniciar e o problema continua
    responses:
      201:
        description: Comentario adicionado com sucesso
      401:
        description: Token ausente ou invalido
      403:
        description: Voce nao tem acesso a este chamado
      404:
        description: Chamado nao encontrado
    """
    usuario = db.session.get(Usuario, get_jwt_identity())
    chamado = db.session.get(Chamado, chamado_id)

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
    """Lista os comentarios de um chamado, do mais antigo ao mais recente.
    ---
    tags:
      - Comentarios
    security:
      - Bearer: []
    parameters:
      - in: path
        name: chamado_id
        type: integer
        required: true
        description: Id do chamado
    responses:
      200:
        description: Lista de comentarios do chamado
      401:
        description: Token ausente ou invalido
      403:
        description: Voce nao tem acesso a este chamado
      404:
        description: Chamado nao encontrado
    """
    usuario = db.session.get(Usuario, get_jwt_identity())
    chamado = db.session.get(Chamado, chamado_id)

    if not chamado:
        return jsonify({"erro": "Chamado nao encontrado"}), 404

    if not usuario_pode_acessar_chamado(usuario, chamado):
        return jsonify({"erro": "Voce nao tem acesso a este chamado"}), 403

    comentarios = Comentario.query.filter_by(chamado_id=chamado.id).order_by(Comentario.data_criacao, Comentario.id).all()

    resultado = []
    for comentario in comentarios:
        resultado.append({
            "id": comentario.id,
            "texto": comentario.texto,
            "usuario_id": comentario.usuario_id,
            "data_criacao": comentario.data_criacao.isoformat()
        })

    return jsonify(resultado), 200

@chamados_bp.route("/metricas", methods=["GET"])
@jwt_required()
def metricas():
    """Resumo dos chamados por status, prioridade e categoria (somente tecnico ou admin).
    ---
    tags:
      - Metricas
    security:
      - Bearer: []
    responses:
      200:
        description: Totais agrupados dos chamados
      401:
        description: Token ausente ou invalido
      403:
        description: Acesso restrito a tecnicos e administradores
    """
    usuario = db.session.get(Usuario, get_jwt_identity())

    if usuario.papel not in ["tecnico", "admin"]:
        return jsonify({"erro": "Acesso restrito a tecnicos e administradores"}), 403

    def contar_por(coluna):
        """Conta quantos chamados existem para cada valor da coluna."""
        linhas = db.session.query(coluna, func.count(Chamado.id)).group_by(coluna).all()
        return {valor: quantidade for valor, quantidade in linhas}

    return jsonify({
        "total": Chamado.query.count(),
        "por_status": contar_por(Chamado.status),
        "por_prioridade": contar_por(Chamado.prioridade),
        "por_categoria": contar_por(Chamado.categoria)
    }), 200