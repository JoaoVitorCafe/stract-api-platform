from flask import Blueprint, jsonify, make_response, abort
from app import relatorios_service


def _criar_resposta_csv(conteudo_csv: str):
    """Função auxiliar para criar a resposta HTTP com o CSV."""
    response = make_response(conteudo_csv)
    response.headers["Content-Disposition"] = "attachment; filename=relatorio.csv"
    response.headers["Content-Type"] = "text/csv"
    return response


def get_valid_platforms() -> list:
    """
    Retorna uma lista com as plataformas válidas obtidas a partir do extrator.
    Caso ocorra algum erro, retorna uma lista vazia.
    """
    try:
        plataformas = relatorios_service.extrator.extrair_todas_plataformas()
        return [p["value"] for p in plataformas]
    except Exception:
        return []
