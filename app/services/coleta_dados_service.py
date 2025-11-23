# app/services/coleta_dados_service.py (Código Atualizado)

from app.utils.database import fazer_consulta_banco
from app.models.dataModel import AnaliseRequest
import logging 

logger = logging.getLogger(__name__)

FK_MAQUINA_TODOS = None 

def coletar_dados_historicos(dados_analise: AnaliseRequest, agrupar_por: str):
    instrucao_sql = """
    CALL sp_coleta_dados_brutos(
        %s,    -- p_data_inicio
        NOW(),    -- p_data_fim
        %s,    -- p_fk_empresa
        %s,    -- p_fk_maquina
        %s,    -- p_agrupar_por
        %s,    -- p_metrica_analisar
        %s     -- p_tipo_componente
    );
    """
    params = (
        dados_analise.dataIncio + " 00:00:00",
        dados_analise.fkEmpresa,
        dados_analise.fkMaquina if dados_analise.fkMaquina is not None else FK_MAQUINA_TODOS,
        agrupar_por,
        dados_analise.metricaAnalisar,
        dados_analise.componente
    )

    logger.info("Parâmetros da SP sendo enviados: %s", params)
    
    try:
        dados_brutos = fazer_consulta_banco({"query": instrucao_sql, "params": params})
        
        if not dados_brutos:
            logger.warning("Coleta de dados retornou 0 resultados. Verificar  os filtros e o DB.")
            
        return dados_brutos if dados_brutos else []
    except RuntimeError as e:
        logger.error("Falha ao coletar dados históricos devido a erro de DB: %s", e)
        return []


def coletar_dados_correlacao(dados_analise: AnaliseRequest, agrupar_por: str, fk_maquina: int = None):
    # ainda a ser realizadpo
    dados_a = coletar_dados_historicos(dados_analise, agrupar_por, fk_maquina)

    # 2. Série B (Variável Relacionada)
    analise_b = AnaliseRequest(
        tipoAnalise=dados_analise.tipoAnalise,
        dataIncio=dados_analise.dataIncio,
        metricaAnalisar=dados_analise.variavelRelacionada,
        dataPrevisao=dados_analise.dataPrevisao,
        componente=dados_analise.componente
    )
    dados_b = coletar_dados_historicos(analise_b, agrupar_por, fk_maquina)
    
    return dados_a, dados_b