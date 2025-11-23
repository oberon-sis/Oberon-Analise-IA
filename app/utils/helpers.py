from datetime import datetime
import logging

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
    # if diferenca_dias <= 1:
    #     return "HORA"
    # elif diferenca_dias <= 60: 
    #     return "DIA"
    # else:
    #     return "MES"
        # Lógica de agrupamento:
    if diferenca_dias <= 1:
        return "HORA"
    elif diferenca_dias <= 60: 
        return "HORA"
    else:
        return "HORA"
    
def formatar_resposta_frontend(
    analise_tipo: str, 
    agrupamento: str, 
    insight_ia: list, 
    lista_metricas: list, 
    grafico_data: dict
) -> dict:
    """
    Padroniza a resposta JSON para o Front-End.
    
    analise_tipo: Tipo da análise (ex: 'previsao', 'correlacao').
    agrupamento: Agrupamento temporal utilizado (ex: 'DIA').
    insight_ia: Lista de strings (parágrafos) gerada pelo Gemini.
    lista_metricas: Lista de objetos {'metrica_titulo': str, 'metrica_valor': str}.
    grafico_data: Dicionário com os dados do gráfico (labels, dataAtual, dataAnterior).
    """
    return {
        "analise_tipo": analise_tipo,
        "agrupamento": agrupamento,
        "iaMetricas": {
            "interpretacao": insight_ia,
            "metricas": lista_metricas 
        },
        "graficoData": grafico_data
    }