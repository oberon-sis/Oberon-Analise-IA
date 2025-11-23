from flask import Blueprint, request, jsonify
from app.models.dataModel import AnaliseRequest
import logging

# Importar as funções de orquestração de cada tipo de análise (Service Layer)
from app.services.analise_previsao import processar_request_previsao
# Assumimos a criação destas funções no futuro para manter o padrão limpo:
# from app.services.analise_comparacao import processar_request_comparacao
# from app.services.analise_correlacao import processar_request_correlacao 

logger = logging.getLogger(__name__)
ai_bp = Blueprint("ai", __name__) # Mantido o nome original 'ai_bp'

def mapear_dados_entrada(dados_entrada: dict) -> AnaliseRequest:
    """Mapeia os dados brutos da requisição HTTP para a dataclass AnaliseRequest."""
    return AnaliseRequest(
        tipoAnalise=dados_entrada.get("tipoAnalise"),
        dataIncio=dados_entrada.get("dataIncio"),
        metricaAnalisar=dados_entrada.get("metricaAnalisar"),
        fkEmpresa=dados_entrada.get("fkEmpresa"),
        fkMaquina=dados_entrada.get("fkMaquina"),
        dataPrevisao=dados_entrada.get("dataPrevisao"),
        componente=dados_entrada.get("componente"),
        variavelRelacionada=dados_entrada.get("variavelRelacionada")
    )

@ai_bp.route("/correlacao", methods=["POST"])
def correlacao():
    """Rota para análise de Correlação (Exemplo de padrão limpo)."""
    try:
        dados_entrada = request.get_json()
        analise_req = mapear_dados_entrada(dados_entrada)
        
        # 1. Validação mínima:
        if not analise_req.variavelRelacionada:
            return jsonify({"erro": "A análise de correlação exige 'variavelRelacionada'."}), 400

        # 2. Delegação ao Service (Service faz TUDO)
        # resultado_final = processar_request_correlacao(analise_req)
        logger.info("Requisição CORRELACAO delegada ao Service.")
        
        # Simulação de retorno
        resultado_final = {"analise_tipo": "correlacao", "resultado": "Funcionalidade em desenvolvimento."}

        if "erro" in resultado_final:
            return jsonify(resultado_final), 400
            
        return jsonify(resultado_final), 200

    except Exception as e:
        logger.error("Erro inesperado na rota /correlacao: %s", e)
        return jsonify({"erro": f"Falha no processamento da requisição: {e}"}), 500


@ai_bp.route("/comparar", methods=["POST"])
def comparar():
    """Rota para análise de Comparação (Exemplo de padrão limpo)."""
    try:
        dados_entrada = request.get_json()
        analise_req = mapear_dados_entrada(dados_entrada)

        # 1. Delegação ao Service (Service faz TUDO)
        # resultado_final = processar_request_comparacao(analise_req)
        logger.info("Requisição COMPARAR delegada ao Service.")

        # Simulação de retorno
        resultado_final = {"analise_tipo": "comparar", "resultado": "Funcionalidade em desenvolvimento."}

        if "erro" in resultado_final:
            return jsonify(resultado_final), 400
            
        return jsonify(resultado_final), 200

    except Exception as e:
        logger.error("Erro inesperado na rota /comparar: %s", e)
        return jsonify({"erro": f"Falha no processamento da requisição: {e}"}), 500


@ai_bp.route("/previsao", methods=["POST"])
def previsao():
    """
    Rota refatorada para Análise de Previsão.
    O Controller apenas recebe, formata e delega.
    """
    try:
        # 1. Receber e estruturar o JSON do front
        dados_entrada = request.get_json()
        
        analise_req = mapear_dados_entrada(dados_entrada)

        # Validação específica da previsão
        if not analise_req.dataPrevisao:
            return jsonify({"erro": "A análise de previsão exige 'dataPrevisao'."}), 400

        # 2. DELEGAR: Chama a função de serviço que faz TUDO (Coleta, Lógica, Gemini)
        resultado_final = processar_request_previsao(analise_req)
        
        # 3. Retornar o resultado do serviço
        if "erro" in resultado_final:
            # Retorna 400 se o Service encontrou um erro de negócio (ex: sem dados)
            return jsonify(resultado_final), 400
            
        # 4. Sucesso: Retorna o JSON formatado pelo Service
        return jsonify(resultado_final), 200

    except Exception as e:
        # Retorna 500 para erros não tratados (ex: erro de Flask, erro de JSON)
        logger.error("Erro inesperado na rota /previsao: %s", e)
        return jsonify({"erro": f"Falha no processamento da requisição: {e}"}), 500


# Rotas de utilidade (se precisar mantê-las separadas por motivos específicos)

# @ai_bp.route("/gemini", methods=["POST"])
# def gemini():
#     # Esta rota pode ser simplificada ou removida se a lógica Gemini for apenas
#     # usada dentro das rotas de análise (previsao, comparacao, correlacao).
#     data = request.get_json()
#     resposta = get_gemini_response(data["prompt"])
#     return jsonify({"resposta": resposta})
# ... (outras rotas de utilidade)