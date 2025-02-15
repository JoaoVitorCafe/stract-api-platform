"""Blueprint para rotas relacionadas a plataformas específicas."""

from flask import Blueprint, jsonify, make_response, abort
from utils.utils import _criar_resposta_csv, get_valid_platforms
from app import relatorios_service

plataformas_bp = Blueprint("plataformas", __name__)


@plataformas_bp.route("/<string:plataforma_value>")
def relatorio_plataforma(plataforma_value: str):
    """
    Retorna um relatório em formato CSV para uma plataforma específica.

    Args:
        plataforma (str): O nome da plataforma (ex: 'meta_ads').
    """

    if plataforma_value not in get_valid_platforms():
        abort(404, description="Plataforma não encontrada.")

    try:
        relatorio_csv = relatorios_service.gerar_relatorio_plataforma(plataforma_value)
        return _criar_resposta_csv(relatorio_csv)

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Erro interno ao gerar relatório."}), 500


@plataformas_bp.route("/<string:plataforma_value>/resumo")
def relatorio_plataforma_resumo(plataforma_value: str):
    """
    Retorna um relatório resumido em formato CSV para uma plataforma específica.

    Args:
        plataforma (str): O nome da plataforma.
    """

    if plataforma_value not in get_valid_platforms():
        abort(404, description="Plataforma não encontrada.")

    try:
        relatorio_csv = relatorios_service.gerar_relatorio_plataforma_resumo(
            plataforma_value
        )
        return _criar_resposta_csv(relatorio_csv)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Erro interno ao gerar relatório."}), 500
