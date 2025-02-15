"""Estrutura principal da API Flask."""

import os
from flask import Flask, jsonify, make_response
from flask_cors import CORS
from dotenv import load_dotenv

from services.relatorios_service import RelatoriosService  # Serviço centralizado
from extratores.extrator_stract import ExtratorDadosStract  # Implementação concreta

# Inicializa o service para criação de relatórios(pode ser usado em várias rotas)
extractor = ExtratorDadosStract()
relatorios_service = RelatoriosService(extractor)


def create_app():
    """Factory function para criar a aplicação Flask."""
    app = Flask(__name__)
    CORS(app)  # Habilitar CORS para todas as origens

    # Carrega as variáveis de ambiente do arquivo .env
    load_dotenv()

    # Importando as blueprints dentro do create_app para evitar problemas com imports circulares
    from blueprints.plataformas_bp import plataformas_bp
    from blueprints.geral_bp import geral_bp

    # Registrando as blueprints
    app.register_blueprint(plataformas_bp)
    app.register_blueprint(geral_bp)

    @app.route("/")
    def index():
        """Rota raiz que retorna informações pessoais."""
        info = {
            "nome": "João Vítor Café dos Reis Batista",
            "email": "batistajv2012@gmail.com",
            "linkedin": "https://www.linkedin.com/in/joaovitorcafe/",
        }
        return jsonify(info)

    # Adicionando manipuladores de erro
    @app.errorhandler(404)
    def not_found(error):
        return make_response(jsonify({"error": "Not found"}), 404)

    @app.errorhandler(500)
    def internal_error(error):
        return make_response(jsonify({"error": "Internal Server Error"}), 500)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)  # Modo de depuração ativado
