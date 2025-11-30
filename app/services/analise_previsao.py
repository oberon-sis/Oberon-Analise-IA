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
    
    ultimo_valor_real = valores_historicos[-1] if valores_historicos else 0
    ultimo_valor_previsto = projecao[-1] if projecao else 0
    confianca = int(resultado_modelo['confiabilidade'])
    nome_modelo = resultado_modelo['nome']
    
    contexto_componente = f" ({analise_req.componente})" if analise_req.componente and analise_req.componente != 'TODOS' else ""
    nome_metrica = f"{analise_req.metricaAnalisar}{contexto_componente}"
    
    risco = "NORMAL"
    if nome_metrica.upper().find('DISCO') > -1 and ultimo_valor_previsto > 90:
        risco = "CRÍTICO"
    elif nome_metrica.upper().find('RAM') > -1 and ultimo_valor_previsto > 85:
        risco = "CRÍTICO"
    elif nome_metrica.upper().find('DOWNTIME') > -1 and ultimo_valor_previsto > 5:
        risco = "CRÍTICO"
    elif ultimo_valor_previsto > ultimo_valor_real * 1.10:
        risco = "ATENÇÃO"


    lista_metricas = [
        {
            "titulo": "Modelo Vencedor",
            "valor": nome_modelo
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
            "valor": f"{confianca}%"
        }
    ]
    
    tipo_de_modelo = {
        "melhorModelo": nome_modelo,
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

    # --- PROMPT ULTRACURTO (Capacity Planning) ---
    prompt_gemini = f"""
    **ROLE:** Engenheiro de Capacidade / SysAdmin.
    **USUÁRIO:** Analista de TI. Use linguagem técnica.
    **REGRAS:** Máximo 30 palavras por parágrafo. Sem introduções.

    **PROJEÇÃO CALCULADA:**
    - Métrica: {nome_metrica}
    - Valor Atual: {ultimo_valor_real:.1f}
    - Projeção Final: {ultimo_valor_previsto:.1f}
    - Risco Determinado: {risco} (Baseado no limite de 85% a 90% para componentes).
    - Confiabilidade do Modelo: {confianca}%

    **OUTPUT JSON (2 strings):**
    1. **Alerta de Capacidade:** Descreva a tendência e o risco futuro. (Ex: "Risco CRÍTICO. A projeção de {nome_metrica} excede o limite de segurança em X dias." ou "Projeção ESTÁVEL, sem risco de saturação.").
    2. **Ação Preventiva:** Dê uma recomendação técnica imediata. (Se CRÍTICO: "Agendar limpeza dos discos ou provisionamento de recurso." Se NORMAL: "Manter monitoramento; a confiabilidade é {confianca}%.").
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