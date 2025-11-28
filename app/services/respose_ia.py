from .coleta_dados_service import coletar_dados_por_intervalo
from .gemini_service import get_gemini_response
from app.models.dataModelIA import IARequest
from app.utils.helpers import calcular_agrupamento, formatar_resposta_frontend_ia
from datetime import datetime, timedelta
import logging
import json
import pandas as pd

logger = logging.getLogger(__name__)

def calcular_periodo_anterior(data_inicio_str, data_fim_str):
    fmt = '%Y-%m-%d'
    try:
        inicio = datetime.strptime(data_inicio_str, fmt)
        fim = datetime.strptime(data_fim_str, fmt) if data_fim_str else datetime.now()
        duracao = fim - inicio
        novo_fim = inicio - timedelta(days=1)
        novo_inicio = novo_fim - duracao
        return novo_inicio.strftime(fmt), novo_fim.strftime(fmt)
    except Exception as e:
        logger.error(f"Erro ao calcular datas: {e}")
        return None, None

def preparar_dataframe_comparacao(dados_brutos):
    if not dados_brutos:
        return pd.DataFrame(columns=['data', 'valor'])
    df = pd.DataFrame(dados_brutos, columns=['data', 'valor'])
    df['data'] = pd.to_datetime(df['data'])
    df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
    if df['valor'].isnull().any():
        df['valor'] = df['valor'].fillna(0)
    return df


def processar_request_pergunta(analise_req: IARequest):
    # define o periodo anterior

    json_schema_ia = {
        "type": "object",
        "properties": {
            "interpretacao": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Lista de 2 parágrafos."
            }
        },
        "required": ["interpretacao"]
    }

    prompt_gemini = analise_req.pergunta
    
    try:
        resposta_ia_json_str = get_gemini_response(prompt_gemini, json_schema_ia)
        ia_data = json.loads(resposta_ia_json_str)
        insight_ia = ia_data.get("interpretacao", ["Análise indisponível."])
    except Exception as e:
        logger.error("Falha Gemini Comparação: %s", e)
        insight_ia = ["Erro na geração de análise."]

    resposta =  formatar_resposta_frontend_ia(
        resposta=insight_ia
    )
    print(resposta)
    return resposta