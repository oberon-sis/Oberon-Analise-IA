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
    
    # Lógica de agrupamento:
    if diferenca_dias <= 1:
        return "HORA"
    elif diferenca_dias <= 60: 
        return "DIA"
    else:
        return "MES"