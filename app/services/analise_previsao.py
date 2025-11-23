# app/services/analise_previsao.py

from .coleta_dados_service import coletar_dados_historicos
from .gemini_service import get_gemini_response
from app.models.dataModel import AnaliseRequest
from datetime import datetime
import logging
from ..utils.helpers import calcular_agrupamento 

logger = logging.getLogger(__name__)


def processar_request_previsao(analise_req: AnaliseRequest):
    """
    Orquestra a coleta, cálculo e análise Gemini para o tipo 'previsao'.
    """
    
    agrupar_por = calcular_agrupamento(analise_req.dataIncio, analise_req.dataPrevisao)
    
    dados_brutos = coletar_dados_historicos(analise_req, agrupar_por)
    
    if not dados_brutos:
        logger.warning("Processamento de Previsão cancelado: dados brutos vazios.")
        return {
            "analise_tipo": "previsao",
            "erro": "Sem dados históricos no período para realizar a previsão."
        }
    
    datas_historico = [str(dado[0]) for dado in dados_brutos]
    valores = [float(dado[1]) for dado in dados_brutos]
    
    logger.debug(datas_historico)
    logger.debug(valores)

    return {
        "analise_tipo": "previsao",
        "agrupamento": agrupar_por,
        "previsao": 'previsoes',
        "historico": valores,
        "datas_historico": datas_historico,
        "insight_ia": 'insight_ia'
    }