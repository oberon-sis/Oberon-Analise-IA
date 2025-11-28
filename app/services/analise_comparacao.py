from .coleta_dados_service import coletar_dados_por_intervalo
from .gemini_service import get_gemini_response
from app.models.dataModel import AnaliseRequest
from app.utils.helpers import calcular_agrupamento, formatar_resposta_frontend
from datetime import datetime, timedelta
import logging
import json
import pandas as pd

logger = logging.getLogger(__name__)

def calcular_periodo_anterior(data_inicio_str, data_fim_str):
    fmt = '%Y-%m-%d'
    try:
        inicio = datetime.strptime(data_inicio_str, fmt)
        fim = datetime.strptime(data_fim_str, fmt) if data_fim_str else datetime.now()
        duracao = fim - inicio
        novo_fim = inicio - timedelta(days=1)
        novo_inicio = novo_fim - duracao
        return novo_inicio.strftime(fmt), novo_fim.strftime(fmt)
    except Exception as e:
        logger.error(f"Erro ao calcular datas: {e}")
        return None, None

def preparar_dataframe_comparacao(dados_brutos):
    if not dados_brutos:
        return pd.DataFrame(columns=['data', 'valor'])
    df = pd.DataFrame(dados_brutos, columns=['data', 'valor'])
    df['data'] = pd.to_datetime(df['data'])
    df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
    if df['valor'].isnull().any():
        df['valor'] = df['valor'].fillna(0)
    return df


def processar_request_comparacao(analise_req: AnaliseRequest):
    # define o periodo anterior
    data_inicio_atual = analise_req.dataIncio
    data_fim_atual = analise_req.dataPrevisao or datetime.now().strftime('%Y-%m-%d')
    
    data_inicio_ant, data_fim_ant = calcular_periodo_anterior(data_inicio_atual, data_fim_atual)
    agrupar_por = calcular_agrupamento(data_inicio_atual, data_fim_atual)
    
    #  Coleta de Dados
    dados_atual = coletar_dados_por_intervalo(analise_req, data_inicio_atual, data_fim_atual, agrupar_por)
    dados_anterior = coletar_dados_por_intervalo(analise_req, data_inicio_ant, data_fim_ant, agrupar_por)
    
    if not dados_atual:
        return {"analise_tipo": "comparacao", "erro": "Sem dados para o período atual selecionado."}

    # 3. Tratamento
    df_atual = preparar_dataframe_comparacao(dados_atual)
    df_anterior = preparar_dataframe_comparacao(dados_anterior)
    
    total_atual = df_atual['valor'].sum()
    total_anterior = df_anterior['valor'].sum() if not df_anterior.empty else 0
    
    media_atual = df_atual['valor'].mean()
    media_anterior = df_anterior['valor'].mean() if not df_anterior.empty else 0
    
    # Delta
    if total_anterior > 0:
        delta_val = total_atual - total_anterior
        delta_pct = (delta_val / total_anterior) * 100
        sinal = "+" if delta_pct > 0 else ""
        delta_str = f"{sinal}{delta_pct:.1f}%"
    else:
        delta_str = "N/A (Sem histórico)"

    lista_metricas = [
        { "titulo": "Total (Atual)", "valor": f"{total_atual:.0f}" },
        { "titulo": "Total (Anterior)", "valor": f"{total_anterior:.0f}" },
        { "titulo": "Variação (%)", "valor": delta_str },
        { "titulo": "Média Diária (Atual)", "valor": f"{media_atual:.1f}" }
    ]
    
    # Dados para o Front
    valores_atual = [float(v) for v in df_atual['valor'].tolist()]
    datas_atual = df_atual['data'].dt.strftime('%d/%m').tolist()
    
    if df_anterior.empty:
        valores_anterior = []
        datas_anterior = []
    else:
        valores_anterior = [float(v) for v in df_anterior['valor'].tolist()]
        datas_anterior = df_anterior['data'].dt.strftime('%d/%m').tolist()

    json_schema_ia = {
        "type": "object",
        "properties": {
            "interpretacao": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Lista de 2 parágrafos."
            }
        },
        "required": ["interpretacao"]
    }

    prompt_gemini = f"""
    Atue como Analista de Performance. Compare a métrica '{analise_req.metricaAnalisar}'.
    - Atual: Total={total_atual:.0f}
    - Anterior: Total={total_anterior:.0f}
    - Variação: {delta_str}
    
    Gere 2 parágrafos curtos para 'interpretacao':
    1. Analise a mudança de comportamento.
    2. Explique se a variação é positiva/negativa e recomende ação.
    """
    
    try:
        resposta_ia_json_str = get_gemini_response(prompt_gemini, json_schema_ia)
        ia_data = json.loads(resposta_ia_json_str)
        insight_ia = ia_data.get("interpretacao", ["Análise indisponível."])
    except Exception as e:
        logger.error("Falha Gemini Comparação: %s", e)
        insight_ia = ["Erro na geração de análise."]

    resposta =  formatar_resposta_frontend(
        analise_tipo="comparacao",
        agrupamento=agrupar_por,
        insight_ia=insight_ia,
        metricas=lista_metricas,
        labels=datas_atual,
        labels_antiga=datas_anterior, # [] se vazio
        data_atual=valores_atual,
        data_antiga=valores_anterior, # [] se vazio
        data_futura=[], 
        tipo_modelo={"tipo": "Comparação Temporal", "metodo": "Delta Percentual"},
        linha_regressao=[]
    )
    print(resposta)
    return resposta