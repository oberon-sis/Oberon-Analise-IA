from .coleta_dados_service import coletar_dados_historicos
from .gemini_service import get_gemini_response
from app.models.dataModel import AnaliseRequest
from app.utils.helpers import calcular_agrupamento, formatar_resposta_frontend
import logging
import json
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


def preparar_datasets_correlacao(dados_a, dados_b):
    """
    Cria dois DataFrames e os alinha pela data (Inner Join).
    Só mantemos registros onde temos dados de AMBAS as métricas.
    """
    if not dados_a or not dados_b:
        return None

    df_a = pd.DataFrame(dados_a, columns=['data', 'valor_a'])
    df_b = pd.DataFrame(dados_b, columns=['data', 'valor_b'])
    
    df_a['data'] = pd.to_datetime(df_a['data'])
    df_b['data'] = pd.to_datetime(df_b['data'])
    
    df_a['valor_a'] = pd.to_numeric(df_a['valor_a'], errors='coerce')
    df_b['valor_b'] = pd.to_numeric(df_b['valor_b'], errors='coerce')

    df_final = pd.merge(df_a, df_b, on='data', how='inner')
    
    df_final = df_final.sort_values('data')
    
    return df_final


def calcular_pearson(df):
    """Calcula o coeficiente de correlação de Pearson."""
    if len(df) < 2:
        return 0
    
    correlacao = df['valor_a'].corr(df['valor_b'])
    return correlacao if not np.isnan(correlacao) else 0

def interpretar_correlacao(r):
    """Helper simples para dar um nome à força da correlação."""
    abs_r = abs(r)
    if abs_r > 0.9: return "Muito Forte"
    if abs_r > 0.7: return "Forte"
    if abs_r > 0.5: return "Moderada"
    if abs_r > 0.3: return "Fraca"
    return "Inexistente/Desprezível"

def calcular_regressao_linear(df):
    """
    Calcula os coeficientes da regressão linear (Y = B0 + B1 * X)
    e gera dois pontos para desenhar a linha no frontend.
    Y = valor_a (Métrica Principal)
    X = valor_b (Variável Relacionada)
    """
    if len(df) < 2:
        return None, None, None

    # Ajuste polinomial de grau 1: [B1 (inclinação), B0 (intercepto)]
    # Usamos X = valor_b e Y = valor_a
    coeficientes = np.polyfit(df['valor_b'], df['valor_a'], 1)
    
    # B1 (inclinação) e B0 (intercepto)
    inclinacao_b1 = coeficientes[0] 
    intercepto_b0 = coeficientes[1]
    
    # -----------------------------------------------------------------
    # Geração dos Pontos para o Gráfico
    
    # Encontra os valores min/max de X (valor_b) para definir a extensão da linha
    x_min = df['valor_b'].min()
    x_max = df['valor_b'].max()

    # Se min e max forem iguais (como no seu exemplo), adicione uma pequena margem
    if x_min == x_max:
        x_min -= 1 
        x_max += 1

    # Calcula os valores Y (valor_a) correspondentes usando a equação: Y = B0 + B1 * X
    y_min = intercepto_b0 + inclinacao_b1 * x_min
    y_max = intercepto_b0 + inclinacao_b1 * x_max

    # Formato de retorno para o frontend
    linha_regressao = [
        {"x": round(float(x_min), 2), "y": round(float(y_min), 2)},
        {"x": round(float(x_max), 2), "y": round(float(y_max), 2)}
    ]
    
    return inclinacao_b1, intercepto_b0, linha_regressao


def processar_request_correlacao(analise_req: AnaliseRequest):
    """
    Orquestra a análise de correlação entre Métrica Principal e Variável Relacionada.
    """
    
    if not analise_req.variavelRelacionada:
        return {"analise_tipo": "correlacao", "erro": "Variável relacionada não fornecida."}

    agrupar_por = calcular_agrupamento(analise_req.dataIncio, analise_req.dataPrevisao)
    
    dados_a = coletar_dados_historicos(analise_req, agrupar_por)
    logging.info("dados_da variavel analisada")
    logging.info(dados_a)
    req_b = AnaliseRequest(
        tipoAnalise=analise_req.tipoAnalise,
        dataIncio=analise_req.dataIncio,
        metricaAnalisar=analise_req.variavelRelacionada,
        fkEmpresa=analise_req.fkEmpresa,
        fkMaquina=analise_req.fkMaquina,
        dataPrevisao=analise_req.dataPrevisao,
        componente=analise_req.componente, 
        variavelRelacionada=None
    )
    dados_b = coletar_dados_historicos(req_b, agrupar_por)
    logging.info("dadod da varivel relacionada: ")
    logging.info(dados_b)
    if not dados_a or not dados_b:
        return {"analise_tipo": "correlacao", "erro": "Sem dados suficientes para uma das variáveis."}

    df = preparar_datasets_correlacao(dados_a, dados_b)
    
    if df is None or len(df) < 2:
        return {"analise_tipo": "correlacao", "erro": "Poucos dados em comum (datas não batem)."}

    inclinacao_b1, intercepto_b0, linha_regressao = calcular_regressao_linear(df)

    pearson_r = calcular_pearson(df)
    intensidade = interpretar_correlacao(pearson_r)
    
    lista_metricas = [
        { "titulo": "Coeficiente de Pearson (r)", "valor": f"{pearson_r:.2f}" },
        { "titulo": "Intensidade", "valor": intensidade },
        { "titulo": "Pontos Analisados", "valor": f"{len(df)}" }
    ]
    
    valores_a = [float(v) for v in df['valor_a'].tolist()]
    valores_b = [float(v) for v in df['valor_b'].tolist()]
    datas_comuns = df['data'].dt.strftime('%d/%m').tolist()

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
    Atue como Cientista de Dados. Analise a correlação entre '{analise_req.metricaAnalisar}' (Variável A) e '{analise_req.variavelRelacionada}' (Variável B).
    
    Dados:
    - Coeficiente de Pearson (r): {pearson_r:.2f} ({intensidade})
    - Regressão Linear: Y = {intercepto_b0:.2f} + {inclinacao_b1:.2f} * X
    - Amostra de Dados A: {valores_a[-5:]}
    - Amostra de Dados B: {valores_b[-5:]}
    
    Gere 2 parágrafos curtos para 'interpretacao':
    1. Explique a relação encontrada (positiva, negativa ou neutra) e sua força.
    2. Dê uma interpretação de negócio: uma métrica influencia a outra? É causa ou coincidência?
    """
    
    try:
        resposta_ia_json_str = get_gemini_response(prompt_gemini, json_schema_ia)
        ia_data = json.loads(resposta_ia_json_str)
        insight_ia = ia_data.get("interpretacao", ["Análise indisponível."])
    except Exception as e:
        logger.error("Falha Gemini Correlação: %s", e)
        insight_ia = ["Erro na geração de análise."]

    # Na correlação, enviamos 'dataAtual' como Métrica A e 'dataAnterior' como Métrica B 
    
    return formatar_resposta_frontend(
        analise_tipo="correlacao",
        agrupamento=agrupar_por,
        insight_ia=insight_ia,
        metricas=lista_metricas,
        labels=datas_comuns,
        data_atual=valores_a,  
        labels_antiga = [],
        data_futura=[],            
        data_antiga=valores_b,  
        tipo_modelo={"tipo": "Correlação Estatística", "metodo": "Pearson"},
        linha_regressao=linha_regressao if linha_regressao else []
    )