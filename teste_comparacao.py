# Exemplo de teste rápido

from app.models.dataModel import AnaliseRequest
from app.services.coleta_dados_service import coletar_dados_historicos
from app.services.analise_comparacao import processar_request_comparacao
import logging

logging.basicConfig(
    level=logging.INFO,
    format='[TESTE - %(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

#teste: total de alertas: ok
#teste: criticos: ok
#teste: Alertas Atenção: ok
#teste: Alertas Ocioso: ok

dados_simulacao = AnaliseRequest(
    tipoAnalise="comparacao",
    dataIncio="2025-10-23",
    metricaAnalisar="total de alertas",
    fkEmpresa= 2, 
    fkMaquina= None,
    dataPrevisao=None,
    componente="CPU",
    variavelRelacionada=None
)

try:
    dados_do_banco = processar_request_comparacao(
        dados_simulacao, 
    )
    
    if "erro" in dados_do_banco:
        logger.warning(" Falha, o serviço retornou um erro: %s", dados_do_banco.get("erro"))
    else:
        logger.info(" Sucesso: O serviço retornou dados de análise.")
        logger.info("--- Detalhes da Resposta ---")
    # Mostra as chaves e o início dos dados, sem tentar iterar como lista
    for chave, valor in dados_do_banco.items():
            if isinstance(valor, list) and len(valor) > 5:
                logger.info(f"- {chave}: [Amostra: {valor[:5]}... Total: {len(valor)} itens]")
            else:
                logger.info(f"- {chave}: {valor}")

except RuntimeError as e:
    logger.error("❌ Erro de Runtime na conexão ou SQL: %s", e)
except Exception as e:
    logger.error("❌ Erro inesperado no script de teste: %s", e)