"""Implementação do extrator de dados usando a API Stract."""

import requests
from typing import List, Dict, Any, Optional
from urllib.parse import urlencode  # Importe urlencode
import os
from dotenv import load_dotenv


class ExtratorDadosStract:
    """Extrator de dados para a API da Stract."""

    BASE_URL = "https://sidebar.stract.to/api"

    def __init__(self):
        load_dotenv()  # Carrega variáveis de ambiente do arquivo .env
        self.TOKEN_AUTORIZACAO = os.getenv(
            "TOKEN_AUTORIZACAO"
        )  # Obtém o token do ambiente
        if not self.TOKEN_AUTORIZACAO:
            raise ValueError(
                "A variável de ambiente TOKEN_AUTORIZACAO não está definida."
            )

    def _fazer_requisicao(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Faz uma requisição GET para a API."""
        headers = {
            "Authorization": f"Bearer {self.TOKEN_AUTORIZACAO}"
        }  # Define o cabeçalho de autorização

        # Adiciona 'page' aos parâmetros, se necessário, mas não sobrescreve se já existir.
        if params is None:
            params = {}
        if "page" not in params:
            params["page"] = 1

        full_url = f"{self.BASE_URL}/{endpoint}"  # Monta a URL base
        if params:
            full_url += "?" + urlencode(
                params
            )  # Adiciona os parâmetros à URL, se houver

        response = requests.get(full_url, headers=headers)  # Faz a requisição GET
        response.raise_for_status()  # Lança exceção para códigos de status de erro (4xx ou 5xx)
        return response.json()  # Retorna a resposta como JSON

    def extrair_contas(self, plataforma: str) -> List[Dict[str, Any]]:
        """Extrai todas as contas de uma plataforma, lidando com paginação."""
        todas_contas = []  # Lista para armazenar todas as contas
        pagina_atual = 1  # Inicializa a página atual
        total_paginas = 1  # Inicializa o total de páginas (será atualizado)

        while pagina_atual <= total_paginas:
            resposta = self._fazer_requisicao(
                "accounts", {"platform": plataforma, "page": pagina_atual}
            )  # Faz a requisição para a página atual
            contas = resposta.get(
                "accounts", []
            )  # Obtém a lista de contas da resposta (ou [] se não houver)
            if not isinstance(
                contas, list
            ):  # Validação: verifica se 'contas' é uma lista
                raise ValueError("Resposta da API para contas não é uma lista.")

            todas_contas.extend(contas)  # Adiciona as contas da página à lista total
            total_paginas = resposta.get("pagination", {}).get(
                "total", 1
            )  # Atualiza o total de páginas (fallback para 1 se não encontrar)
            pagina_atual += 1  # Incrementa a página atual

        return todas_contas  # Retorna a lista completa de contas

    def extrair_campos(self, plataforma: str) -> List[Dict[str, str]]:
        """Extrai todos os campos de uma plataforma, lidando com paginação."""
        todos_campos = []  # Lista para armazenar todos os campos
        pagina_atual = 1  # Inicializa a página atual
        total_paginas = 1  # Inicializa o total de páginas

        while pagina_atual <= total_paginas:
            resposta = self._fazer_requisicao(
                "fields", {"platform": plataforma, "page": pagina_atual}
            )  # Faz a requisição para a página atual
            campos = resposta.get("fields", [])  # Obtém a lista de campos da resposta
            if not isinstance(campos, list):  # Validação
                raise ValueError("Resposta da API para campos não é uma lista.")

            todos_campos.extend(campos)  # Adiciona os campos da página à lista total
            total_paginas = resposta.get("pagination", {}).get(
                "total", 1
            )  # Atualiza o total
            pagina_atual += 1  # Incrementa a página

        return todos_campos  # Retorna a lista completa de campos

    def extrair_insights(
        self, plataforma: str, conta: Dict[str, Any], campos: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """Extrai os insights de uma conta, com tratamento de erros e lista vazia."""
        # Validações:
        if not conta or "token" not in conta or "id" not in conta:
            raise ValueError("Dados da conta inválidos.")
        if not isinstance(campos, list):
            raise TypeError("'campos' deve ser uma lista de dicionários.")

        # Formata a lista de campos corretamente para a URL:
        campos_str = ",".join(
            [
                campo["value"]
                for campo in campos
                if isinstance(campo, dict) and "value" in campo
            ]
        )

        try:
            resposta = self._fazer_requisicao(
                "insights",
                {
                    "platform": plataforma,
                    "account": conta["id"],
                    "token": conta["token"],
                    "fields": campos_str,
                },
            )  # Faz a requisição
        except requests.exceptions.HTTPError as e:  # Captura erros HTTP específicos
            if e.response.status_code == 404:  # Se a conta não for encontrada (404)
                return []  # Retorna uma lista vazia
            else:
                raise
        except (
            requests.exceptions.RequestException
        ) as e:  # Captura outros erros de requisição
            print(f"Erro na requisição: {e}")  # Log do erro
            raise

        insights = resposta.get("insights", [])  # Obtém os insights da resposta
        if not isinstance(insights, list):  # Validação
            raise ValueError("Resposta da API para insights não é uma lista.")

        # Remove insights nulos/vazios (se existirem):
        insights_validos = [insight for insight in insights if insight]
        return insights_validos  # Retorna a lista de insights válidos

    def extrair_todas_plataformas(self) -> List[Dict[str, str]]:
        """Extrai todas as plataformas disponíveis."""
        resposta = self._fazer_requisicao("platforms")  # Faz a requisição
        plataformas = resposta.get("platforms", [])  # Obtém a lista de plataformas
        if not isinstance(plataformas, list):  # Validação
            raise ValueError("Resposta da API para plataformas não é uma lista.")
        return plataformas  # Retorna a lista de plataformas
