from .coleta_dados_service import coletar_dados_historicos
from .gemini_service import get_gemini_response
from app.models.dataModel import AnaliseRequest
from app.utils.helpers import calcular_agrupamento, formatar_resposta_frontend, preparar_dataframe
import logging
import json
import random
import numpy as np
import pandas as pd

# Modelos de Machine Learning
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import RandomForestRegressor 
from sklearn.metrics import r2_score, mean_squared_error
from statsmodels.tsa.holtwinters import ExponentialSmoothing

logger = logging.getLogger(__name__)


def treinar_regressao_linear(df, passos_futuros):
    """Modelo 1: Linear (Tendências retas)."""
    df['data_ordinal'] = df['data'].map(pd.Timestamp.toordinal)
    X = df[['data_ordinal']].values
    y = df['valor'].values
    
    modelo = LinearRegression()
    modelo.fit(X, y)
    y_pred = modelo.predict(X)
    
    r2 = r2_score(y, y_pred)
    rmse = np.sqrt(mean_squared_error(y, y_pred))
    
    ultima_data = df['data'].iloc[-1]
    datas_futuras = [ultima_data + pd.Timedelta(days=i) for i in range(1, passos_futuros + 1)]
    X_futuro = np.array([d.toordinal() for d in datas_futuras]).reshape(-1, 1)
    y_futuro = modelo.predict(X_futuro)

    coef = modelo.coef_[0]
    intercept = modelo.intercept_
    sinal = "+" if intercept >= 0 else "-"
    equacao = f"Equação para o gráfico:  f(x) = {coef:.2f}x {sinal} {abs(intercept):.2f}"

    return {
        "nome": "Regressão Linear",
        "equacao": equacao,
        "rmse": float(rmse),
        "r2": float(r2),
        "projecao": [float(round(val, 2)) for val in y_futuro],
        "confiabilidade": min(max(r2 * 100, 0), 99)
    }

def treinar_polinomial(df, passos_futuros, grau=2):
    """Modelo 2: Polinomial (Curvas suaves)."""
    df['data_ordinal'] = df['data'].map(pd.Timestamp.toordinal)
    X = df[['data_ordinal']].values
    y = df['valor'].values

    modelo = make_pipeline(PolynomialFeatures(grau), LinearRegression())
    modelo.fit(X, y)
    y_pred = modelo.predict(X)

    r2 = r2_score(y, y_pred)
    rmse = np.sqrt(mean_squared_error(y, y_pred))

    ultima_data = df['data'].iloc[-1]
    datas_futuras = [ultima_data + pd.Timedelta(days=i) for i in range(1, passos_futuros + 1)]
    X_futuro = np.array([d.toordinal() for d in datas_futuras]).reshape(-1, 1)
    y_futuro = modelo.predict(X_futuro)

    return {
        "nome": f"Polinomial (Grau {grau})",
        "equacao": f"Equação para o gráfico: f(x) = ax^{grau} + bx + c",
        "rmse": float(rmse),
        "r2": float(r2),
        "projecao": [float(round(val, 2)) for val in y_futuro],
        "confiabilidade": min(max(r2 * 100, 0), 99)
    }

def treinar_random_forest(df, passos_futuros):
    """Modelo 3: Random Forest (Padrões complexos/irregulares)."""
    df['data_ordinal'] = df['data'].map(pd.Timestamp.toordinal)
    X = df[['data_ordinal']].values
    y = df['valor'].values

    # n_estimators=100: 100 arvores de decisão
    # random_state=42: como se fosse a semente no r
    modelo = RandomForestRegressor(n_estimators=100, random_state=42)
    modelo.fit(X, y)
    y_pred = modelo.predict(X)

    r2 = r2_score(y, y_pred)
    rmse = np.sqrt(mean_squared_error(y, y_pred))

    ultima_data = df['data'].iloc[-1]
    datas_futuras = [ultima_data + pd.Timedelta(days=i) for i in range(1, passos_futuros + 1)]
    X_futuro = np.array([d.toordinal() for d in datas_futuras]).reshape(-1, 1)
    y_futuro = modelo.predict(X_futuro)

    
    equacao = "Média de Árvores de Decisão (Não-Paramétrico)"

    return {
        "nome": "Random Forest",
        "equacao": equacao,
        "rmse": float(rmse),
        "r2": float(r2),
        "projecao": [float(round(val, 2)) for val in y_futuro],
        "confiabilidade": min(max(r2 * 100, 0), 99)
    }

def treinar_holt(df, passos_futuros):
    """Modelo 4: Holt (Séries temporais com nível e tendência)."""
    try:
        y = df['valor'].values
        if len(y) < 4: return None
             
        modelo = ExponentialSmoothing(y, trend='add', seasonal=None, damped_trend=True).fit()
        y_pred = modelo.fittedvalues
        
        rmse = np.sqrt(mean_squared_error(y, y_pred))
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        y_futuro = modelo.forecast(passos_futuros)

        return {
            "nome": "Suavização Exponencial (Holt)",
            "equacao": "Equação para o gráfico: Lt = αYt + (1-α)(Lt-1 + Tt-1)",
            "rmse": float(rmse),
            "r2": float(r2),
            "projecao": [float(round(val, 2)) for val in y_futuro],
            "confiabilidade": min(max(r2 * 100, 0), 99)
        }
    except:
        return None

def selecionar_melhor_modelo(df, passos_futuros=5):
    candidatos = []
    candidatos.append(treinar_regressao_linear(df.copy(), passos_futuros))
    candidatos.append(treinar_polinomial(df.copy(), passos_futuros))
    
    candidatos.append(treinar_random_forest(df.copy(), passos_futuros))
    res_holt = treinar_holt(df.copy(), passos_futuros)
    if res_holt:
        candidatos.append(res_holt)
        
    melhor_resultado = sorted(candidatos, key=lambda x: x['rmse'])[0]
    return melhor_resultado


def processar_request_previsao(analise_req: AnaliseRequest):
    agrupar_por = calcular_agrupamento(analise_req.dataIncio, analise_req.dataPrevisao)
    dados_brutos = coletar_dados_historicos(analise_req, agrupar_por)
    
    if not dados_brutos:
        return {"analise_tipo": "previsao", "erro": "Sem dados históricos."}
    
    df = preparar_dataframe(dados_brutos)
    if df is None or len(df) < 5:
        return {"analise_tipo": "previsao", "erro": "Dados insuficientes (mínimo 5 pontos)."}

    valores_historicos = [float(v) for v in df['valor'].tolist()]
    datas_historico = df['data'].dt.strftime('%d/%m').tolist()

    passos_previsao = 5
    resultado_modelo = selecionar_melhor_modelo(df, passos_previsao) 
    projecao = resultado_modelo['projecao']
    
    lista_metricas = [
        {
            "titulo": "Modelo Utilizado",
            "valor": resultado_modelo['nome']
        },
        {
            "titulo": "Precisão (R²)",
            "valor": f"{resultado_modelo['r2']:.2f}"
        },
        {
            "titulo": "Taxa de Erro (RMSE)", 
            "valor": f"{resultado_modelo['rmse']:.2f}"
        },
        {
            "titulo": "Confiabilidade",
            "valor": f"{int(resultado_modelo['confiabilidade'])}%"
        }
    ]
    
    tipo_de_modelo = {
        "melhorModelo": resultado_modelo['nome'],
        "equacao": resultado_modelo['equacao']
    }

    json_schema_ia = {
        "type": "object",
        "properties": {
            "interpretacao": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Lista de 2 parágrafos curtos."
            }
        },
        "required": ["interpretacao"]
    }

    prompt_gemini = f"""
    Analise a previsão para '{analise_req.metricaAnalisar}'.
    Dados:
    - Histórico (últimos): {valores_historicos[-5:]}
    - Projeção: {projecao}
    - Modelo Vencedor: {tipo_de_modelo['melhorModelo']}
    - Erro (RMSE): {resultado_modelo['rmse']:.2f}
    - Precisão (R²): {resultado_modelo['r2']:.2f}
    
    Gere 2 parágrafos curtos para 'interpretacao':
    1. Análise da tendência e projeção futura.
    2. Comentário sobre a confiabilidade do modelo e recomendação.
    """
    
    try:
        resposta_ia_json_str = get_gemini_response(prompt_gemini, json_schema_ia)
        ia_data = json.loads(resposta_ia_json_str)
        insight_ia = ia_data.get("interpretacao", ["Análise indisponível."])
    except Exception as e:
        logger.error("Falha Gemini: %s", e)
        insight_ia = ["Erro na geração de insight."]

    labels_futuros = [f"Futuro {i+1}" for i in range(passos_previsao)]
    labels_totais = datas_historico + labels_futuros
    
    return formatar_resposta_frontend(
        analise_tipo="previsao",
        agrupamento=agrupar_por,
        insight_ia=insight_ia,
        metricas=lista_metricas, 
        labels=labels_totais,
        data_atual=valores_historicos,
        labels_antiga = [],
        data_antiga = [],
        data_futura=projecao, 
        tipo_modelo=tipo_de_modelo,
        linha_regressao = []
    )