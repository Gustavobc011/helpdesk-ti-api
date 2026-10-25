"""Funcoes de validacao de entrada, reaproveitadas pelas rotas da API.

Ideia geral: cada funcao "validar_..." devolve uma mensagem de erro (texto)
quando o valor e invalido, ou None quando esta tudo certo. A rota junta as
mensagens numa lista e, se houver alguma, responde 400 (Bad Request).
"""
import re

from flask import request, jsonify

TAMANHO_MINIMO_SENHA = 6
TAMANHO_MAXIMO_SENHA = 128

# Regex simples de e-mail: "algo@algo.algo", sem espacos e com um unico @.
# Nao cobre 100% dos casos da RFC, mas barra os erros comuns de digitacao.
REGEX_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def ler_json():
    """Le o corpo da requisicao como JSON e sempre devolve um dicionario.

    silent=True faz o Flask devolver None em vez de levantar erro quando o
    corpo nao e JSON valido. Nesse caso (ou se vier uma lista, por exemplo)
    devolvemos {} e as validacoes de campo obrigatorio cuidam do resto.
    """
    dados = request.get_json(silent=True)
    return dados if isinstance(dados, dict) else {}


def validar_texto(dados, campo, maximo=None, obrigatorio=True):
    """Valida um campo de texto: presenca, tipo e tamanho maximo."""
    valor = dados.get(campo)

    # Ausente, null ou so espacos conta como "nao preenchido"
    if valor is None or (isinstance(valor, str) and not valor.strip()):
        return f"O campo '{campo}' e obrigatorio" if obrigatorio else None

    if not isinstance(valor, str):
        return f"O campo '{campo}' deve ser um texto"

    if maximo is not None and len(valor.strip()) > maximo:
        return f"O campo '{campo}' deve ter no maximo {maximo} caracteres"

    return None


def email_valido(email):
    """Retorna True se o e-mail tiver um formato aceitavel."""
    return isinstance(email, str) and REGEX_EMAIL.match(email) is not None


def validar_email(dados, campo="email", maximo=120):
    """Valida presenca, tamanho e formato do e-mail."""
    erro = validar_texto(dados, campo, maximo=maximo)
    if erro:
        return erro
    if not email_valido(dados[campo].strip()):
        return f"O campo '{campo}' deve ser um e-mail valido"
    return None


def validar_senha(dados, campo="senha"):
    """Valida presenca e tamanho da senha (minimo e maximo)."""
    senha = dados.get(campo)
    if not senha:
        return f"O campo '{campo}' e obrigatorio"
    if not isinstance(senha, str):
        return f"O campo '{campo}' deve ser um texto"
    if len(senha) < TAMANHO_MINIMO_SENHA:
        return f"A senha deve ter pelo menos {TAMANHO_MINIMO_SENHA} caracteres"
    if len(senha) > TAMANHO_MAXIMO_SENHA:
        return f"A senha deve ter no maximo {TAMANHO_MAXIMO_SENHA} caracteres"
    return None


def validar_opcao(dados, campo, opcoes):
    """Valida um campo opcional que, se vier, precisa estar na lista de opcoes."""
    valor = dados.get(campo)
    if valor is not None and valor not in opcoes:
        return f"O campo '{campo}' deve ser um de: {', '.join(opcoes)}"
    return None


def resposta_de_erro(*erros):
    """Recebe varios resultados de validacao (mensagens ou None).

    Se houver ao menos uma mensagem, devolve a resposta 400 pronta.
    Se estiver tudo valido, devolve None e a rota segue normalmente.
    """
    mensagens = [erro for erro in erros if erro]
    if mensagens:
        return jsonify({"erro": "Dados invalidos", "detalhes": mensagens}), 400
    return None
