from datetime import datetime
import logging
import pandas as pd

logger = logging.getLogger(__name__)
def calcular_agrupamento(data_inicio_str: str, data_fim_str: str) -> str:
    """
    Determina o agrupamento (HORA, DIA, MES) baseado na duração do histórico.
    Formato da string de data esperado: AAAA-MM-DD
    """
    try:
        data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d')
        data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d')
        diferenca_dias = (data_fim - data_inicio).days
    except ValueError:
        logger.error("Formato de data inválido para cálculo de agrupamento.")
        return "DIA"
    
    # # Lógica de agrupamento:
    if diferenca_dias <= 1:
        return "HORA"
    elif diferenca_dias <= 200: 
        return "DIA"
    else:
        return "MES"
        # Lógica de agrupamento:
    # if diferenca_dias <= 1: # COloca hora para tester lembrar de remover
    #     return "HORA"
    # elif diferenca_dias <= 60: 
    #     return "HORA"
    # else:
    #     return "HORA"
    
def formatar_resposta_frontend(
    analise_tipo: str, 
    agrupamento: str, 
    insight_ia: list, 
    metricas: list,
    labels: list,
    data_atual: list,
    labels_antiga: list,
    data_antiga: list,
    data_futura: list = None,
    tipo_modelo: dict = None,
    linha_regressao: list = None
) -> dict:
    """
    Padroniza a resposta JSON para o Front-End conforme estrutura solicitada.
    """
    return {
        "analise_tipo": analise_tipo,
        "agrupamento": agrupamento,
        "iaMetricas": {
            "interpretacao": insight_ia,
            "chave_metricas": metricas 
        },
        "graficoData": {
            "labels_Data": labels,
            "labels_Data_Antiga": labels_antiga if labels_antiga else [],
            "dataAtual": data_atual,
            "dataAnterior": data_antiga if data_antiga else [],      
            "dataFutura": data_futura if data_futura else []
        },
        "tipo_de_modelo": tipo_modelo if tipo_modelo else {},
        "linha_regressao": linha_regressao
    }


def preparar_dataframe(dados_brutos):
    """ preparar dads em um data frame para um tratamento melhor de dados"""
    if not dados_brutos:
        return None
    df = pd.DataFrame(dados_brutos, columns=['data', 'valor'])
    df['data'] = pd.to_datetime(df['data'])
    df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
    df = df.sort_values('data')
    if df['valor'].isnull().any():
        df['valor'] = df['valor'].interpolate(method='linear').fillna(method='bfill').fillna(method='ffill')
    return df


def formatar_resposta_frontend_ia(
    resposta: str, 
) -> dict:
    """
    Padroniza a resposta JSON para o Front-End conforme estrutura solicitada.
    """
    return {
        "resposta": resposta,
    }