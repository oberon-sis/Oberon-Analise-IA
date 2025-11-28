from app.models.dataModel import AnaliseRequest
from app.services.analise_correlacao import processar_request_correlacao
import logging

logging.basicConfig(
    level=logging.INFO,
    format='[TESTE - %(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


dados_simulacao = AnaliseRequest(
    tipoAnalise="correlacao",
    dataIncio="2025-08-26",
    dataPrevisao="2025-12-03", # Data fim obrigatória
    
    # CORRIJA AQUI: Use um nome que seu SP conhece.
    # Se sua SP não tem 'Downtime' implementado, use 'Total de Alertas' vs 'Uso CPU' para testar
    metricaAnalisar="Uptime", 
    variavelRelacionada="Total de Alertas",      
    
    fkEmpresa=2, 
    fkMaquina=None, 
    componente="RAM"
)

try:
    logger.info("=== Iniciando Teste de Correlação ===")
    resultado = processar_request_correlacao(dados_simulacao)
    
    if "erro" in resultado:
        logger.warning("❌ Falha: %s", resultado.get("erro"))
    else:
        logger.info("✅ Sucesso!")
        # ... (restante do log)
        for chave, valor in resultado.items():
             if chave == "iaMetricas":
                 logger.info(f"- Insight: {valor}")
             else:
                 logger.info(f"- {chave}: {valor}")

except Exception as e:
    logger.error("❌ Erro inesperado: %s", e)