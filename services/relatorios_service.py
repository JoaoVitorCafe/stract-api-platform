"""Serviço para gerar os relatórios."""

from typing import List, Dict, Any, Optional
import pandas as pd
import io
import os
from datetime import datetime
from extratores.extrator_stract import ExtratorDadosStract  # Implementação concreta
from constants.diretorios import CSV_DIR


class RelatoriosService:
    """Serviço para gerar relatórios em formato CSV usando DataFrames."""

    def __init__(self, extrator: Optional[ExtratorDadosStract] = None):
        # Injeção de dependência do extrator. Se nenhum for fornecido, usa a implementação padrão.
        self.extrator = extrator or ExtratorDadosStract()
        # Cria o diretório de CSVs se ele não existir (exist_ok=True evita erro se já existir).
        os.makedirs(CSV_DIR, exist_ok=True)

    def _gerar_e_salvar_csv(self, df: pd.DataFrame, nome_base: str) -> str:
        """Gera uma string CSV a partir de um DataFrame, salvando em arquivo."""
        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )  # Formato: AnoMesDia_HoraMinutoSegundo
        nome_arquivo = f"{timestamp}_{nome_base}.csv"  # Nome do arquivo com timestamp
        caminho = os.path.join(CSV_DIR, nome_arquivo)  # Caminho completo do arquivo

        # Dropa a coluna de id
        df = df.drop("id", axis=1)

        df.to_csv(caminho, index=False)  # Salva o DataFrame como CSV (sem o índice)
        print(f"Relatório salvo em: {caminho}")  # Log informativo

        output = io.StringIO()  # Cria um "arquivo" em memória (string)
        df.to_csv(output, index=False)  # Escreve o DataFrame como CSV na string
        return output.getvalue()  # Retorna a string CSV

    def _extrair_insights_conta(
        self,
        plataforma: str,
        conta: Dict[str, Any],
        campos: List[Dict[str, Any]],
        platform_text: Optional[str] = None,  # Nome da plataforma (opcional)
    ) -> Optional[pd.DataFrame]:
        """Extrai os insights de uma conta, renomeia as colunas e adiciona informações."""
        insights = self.extrator.extrair_insights(
            plataforma, conta, campos
        )  # Obtém os insights da API
        if not insights:
            return None  # Retorna None se não houver insights

        df = pd.DataFrame(insights)  # Cria um DataFrame a partir dos insights
        # Renomeia as colunas do DataFrame (usa o 'text' dos campos, em vez do 'value')
        df.rename(columns={c["value"]: c["text"] for c in campos}, inplace=True)
        if platform_text:
            df["Plataforma"] = (
                platform_text  # Adiciona coluna 'Plataforma' se o nome for fornecido
            )
        df["Conta"] = conta["name"]  # Adiciona a coluna 'Conta'

        # Calcula 'Cost per Click' se compute_cpc for True e as colunas necessárias existirem
        if (
            "Cost Per Click" not in df.columns
            and "Spend" in df.columns
            and "Clicks" in df.columns
        ):
            df["Cost Per Click"] = df.apply(
                lambda row: (
                    row["Spend"] / row["Clicks"] if row["Clicks"] != 0 else 0
                ),  # Evita divisão por zero
                axis=1,  # Aplica a função linha a linha
            )
        return df  # Retorna o DataFrame modificado

    def _process_platform(
        self,
        plataforma: str,
    ) -> pd.DataFrame:
        """Processa todas as contas de uma plataforma e retorna um DataFrame consolidado."""

        platform_val = plataforma["value"]  # Valor da plataforma (ex: 'meta_ads')
        platform_text = plataforma["text"]  # Nome da plataforma (ex: 'Facebook Ads')

        df_total = pd.DataFrame()  # DataFrame vazio para armazenar os resultados
        contas = self.extrator.extrair_contas(
            platform_val
        )  # Obtém as contas da plataforma
        campos = self.extrator.extrair_campos(
            platform_val
        )  # Obtém os campos da plataforma

        for conta in contas:
            # Extrai os insights para cada conta e adiciona ao DataFrame total
            df_insights = self._extrair_insights_conta(
                platform_val, conta, campos, platform_text
            )
            if df_insights is not None:
                df_total = pd.concat(
                    [df_total, df_insights], ignore_index=True
                )  # Concatena (ignore_index=True)

        # Garante a ordem correta das colunas no DataFrame final
        if not df_total.empty:
            cols = ["Plataforma", "Conta"] + [
                col for col in df_total.columns if col not in ["Plataforma", "Conta"]
            ]

            df_total = df_total[cols]  # Reordena as colunas
        return df_total  # Retorna o DataFrame completo

    def _gerar_relatorio_base(self, plataforma: Optional[str] = None) -> pd.DataFrame:
        """
        Gera o DataFrame base do relatório.
        Se 'plataforma' for informado, gera relatório específico; caso contrário, gera relatório geral.
        """

        plataformas = (
            self.extrator.extrair_todas_plataformas()
        )  # Obtém todas as plataformas

        if plataforma:
            plataforma = [p for p in plataformas if p.get("value") == plataforma]
            # Se 'plataforma' foi especificada
            return self._process_platform(
                plataforma[0]
            )  # Retorna o relatório da plataforma

        # Se 'plataforma' não foi especificada, gera o relatório geral
        df_total = pd.DataFrame()

        for plataforma in plataformas:
            # Processa cada plataforma e adiciona ao DataFrame total
            df_plat = self._process_platform(plataforma=plataforma)
            df_total = pd.concat([df_total, df_plat], ignore_index=True)  # Concatena

        # Garante a ordem das colunas para o relatório geral
        if not df_total.empty:
            cols = ["Plataforma", "Conta"] + [
                col for col in df_total.columns if col not in ["Plataforma", "Conta"]
            ]
            df_total = df_total[cols]  # Reordena
        return df_total  # Retorna o DataFrame completo

    def _gerar_resumo(
        self, df: pd.DataFrame, group_by: str, resumo_plataforma: Optional[bool] = None
    ) -> pd.DataFrame:
        """
        Gera um resumo agregando os campos numéricos por 'group_by' (e 'Plataforma', se aplicável).
        Mantém as colunas de agrupamento e preenche as demais colunas não numéricas com string vazia.
        """
        if df.empty:
            return pd.DataFrame(columns=[group_by])

        num_cols = df.select_dtypes(include=["number"]).columns.tolist()

        # Determina as colunas de agrupamento
        if resumo_plataforma:
            group_cols = [group_by, "Plataforma"]
        else:
            group_cols = [group_by]

        # 1. Agrupa e soma:
        resumo = df.groupby(group_cols, as_index=False)[num_cols].sum()

        # 2. Garante que TODAS as colunas originais estejam presentes (preenchendo com NaN):
        resumo = resumo.reindex(columns=df.columns)

        # 3. Preenche NaN com '' APENAS nas colunas que não são numéricas
        #    E não são colunas de agrupamento:
        for col in resumo.columns:
            if col not in num_cols and col not in group_cols:
                resumo[col] = resumo[col].fillna("")

        return resumo

    def gerar_relatorio_plataforma(self, plataforma_value: str) -> str:
        """Gera relatório completo para uma plataforma e retorna a string CSV."""
        df = self._gerar_relatorio_base(plataforma_value)  # Gera o DataFrame base
        return self._gerar_e_salvar_csv(
            df, f"relatorio_{plataforma_value}"
        )  # Gera e salva o CSV

    def gerar_relatorio_plataforma_resumo(self, plataforma_value: str) -> str:
        """Gera relatório resumido por conta para uma plataforma."""
        df = self._gerar_relatorio_base(plataforma_value)  # Gera o DataFrame base
        resumo = self._gerar_resumo(
            df, "Conta", resumo_plataforma=True
        )  # Gera o resumo por conta
        return self._gerar_e_salvar_csv(
            resumo, f"relatorio_{plataforma_value}_resumo"
        )  # Gera e salva o CSV

    def gerar_relatorio_geral(self) -> str:
        """Gera relatório geral de todas as plataformas."""
        df = (
            self._gerar_relatorio_base()
        )  # Gera o DataFrame base (sem especificar plataforma)
        return self._gerar_e_salvar_csv(df, "relatorio_geral")  # Gera e salva o CSV

    def gerar_relatorio_geral_resumo(self) -> str:
        """Gera relatório geral resumido por plataforma."""
        df = (
            self._gerar_relatorio_base()
        )  # Gera o DataFrame base (sem especificar plataforma)
        resumo = self._gerar_resumo(df, "Plataforma")  # Gera o resumo por plataforma
        return self._gerar_e_salvar_csv(
            resumo, "relatorio_geral_resumo"
        )  # Gera e salva o CSV
