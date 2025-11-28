# Exemplo de teste rápido

from app.models.dataModelIA import IARequest
from app.services.respose_ia import processar_request_pergunta
import logging

logging.basicConfig(
    level=logging.INFO,
    format='[TESTE - %(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)



dados_simulacao = IARequest(
    pergunta="o que significa bruna em portugués",
)

try:
    dados_do_banco = processar_request_pergunta(
        dados_simulacao, 
    )
    
    if "erro" in dados_do_banco:
        logger.warning(" Falha, o serviço retornou um erro: %s", dados_do_banco.get("erro"))
    else:
        logger.info(" Sucesso: O serviço retornou dados de análise.")
        logger.info("--- Detalhes da Resposta ---")
        logger.info(f"- {dados_do_banco}")

except RuntimeError as e:
    logger.error("❌ Erro de Runtime na conexão ou SQL: %s", e)
except Exception as e:
    logger.error("❌ Erro inesperado no script de teste: %s", e)