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
    return processar_dados_front_end()

def processar_dados_front_end():
    """
    resultado esperado enviar um json formtado assim para o front end
    response = {
    iaMetricas: {
        interpretacao: [
            'Após o pico de Abril, o Downtime estabilizou-se em torno de 55. A projeção (Mock) indica um aumento gradual para 65 até Setembro, sugerindo atenção imediata.',
            'A análise desta tendência de alertas foi realizada utilizando Regressão Linear sobre o histórico semanal de dados. O Índice de Confiabilidade do modelo é de 85%, indicando alta aderência da projeção à variação real observada.',
        ],
        metricasRegressao: { R: '0.92', R2: '0.85', RSE: '5.2%', indiceConfiabilidade: '85%' },
    },
    graficoData: {
        labels_Dia: ['1 Nov', '2 Nov', '3 Nov', '4 Nov', '5 Nov', '6 Nov', '7 Nov'],
        labels_Semana: ['Sem 44', 'Sem 45', 'Sem 46', 'Sem 47', 'Sem 48', 'Sem 49'],
        labels_Mês: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
        dataAtual: [65, 59, 80, 81, 56, 55],
        dataAnterior: [50, 45, 70, 75, 40, 42],
    },
    
    """

    # return {
    #     "analise_tipo": "previsao",
    #     "agrupamento": agrupar_por,
    #     "previsao": 'previsoes',
    #     "historico": valores,
    #     "datas_historico": datas_historico,
    #     "insight_ia": 'insight_ia'
    # }
    return { #teste
        "analise_tipo": "previsao",
        "agrupamento": "agrupar_por",
        "previsao": 'previsoes',
        "historico": "valores",
        "datas_historico": "datas_historico",
        "insight_ia": 'insight_ia'
    }