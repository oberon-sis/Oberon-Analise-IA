# Exemplo de teste rápido

from app.models.dataModel import AnaliseRequest
from app.services.coleta_dados_service import coletar_dados_historicos
import logging

logging.basicConfig(
    level=logging.INFO,
    format='[TESTE - %(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)



dados_simulacao = AnaliseRequest(
    tipoAnalise="previsao",
    dataIncio="2025-10-23",
    metricaAnalisar="Total de Alertas",
    fkEmpresa= 1, 
    fkMaquina= None,
    dataPrevisao="2025-12-23",
    componente=None,
)

try:
    dados_do_banco = coletar_dados_historicos(
        dados_simulacao, 
        agrupar_por="HORA", 
    )
    
    logger.info("Dados Brutos Recebidos: %s", dados_do_banco)
    
    if dados_do_banco:
        logger.info("Sucesso: houve sim uma respota correta do banco")
        for i in range(min(5, len(dados_do_banco))):
            logger.info(dados_do_banco[i])
    else:
        logger.warning("Falha, retornou vazio as credenciais ou a Stored Procedure.")
except RuntimeError as e:
    logger.error("❌ Erro de Runtime na conexão ou SQL: %s", e)