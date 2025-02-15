"""Blueprint para rotas de relatórios gerais."""

from flask import Blueprint, jsonify, make_response
from utils.utils import _criar_resposta_csv, get_valid_platforms
from app import relatorios_service

geral_bp = Blueprint("geral", __name__)


@geral_bp.route("/geral")
def relatorio_geral():
    """Retorna um relatório geral em formato CSV para todas as plataformas."""

    try:
        relatorio_csv = relatorios_service.gerar_relatorio_geral()
        return _criar_resposta_csv(relatorio_csv)
    except Exception as e:
        return jsonify({"error": "Erro interno ao gerar relatório."}), 500


@geral_bp.route("/geral/resumo")
def relatorio_geral_resumo():
    """Retorna um relatório geral resumido em formato CSV para todas as plataformas."""
    try:
        relatorio_csv = relatorios_service.gerar_relatorio_geral_resumo()
        return _criar_resposta_csv(relatorio_csv)
    except Exception as e:
        return jsonify({"error": "Erro interno ao gerar relatório."}), 500
