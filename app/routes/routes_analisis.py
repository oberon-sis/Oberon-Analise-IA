from flask import Blueprint, request, jsonify
from app.models.dataModel import AnaliseRequest
import logging

from app.services.analise_previsao import processar_request_previsao
from app.services.analise_comparacao import processar_request_comparacao
from app.services.analise_correlacao import processar_request_correlacao 

logger = logging.getLogger(__name__)
ai_bp = Blueprint("ai", __name__)

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
    try:
        dados_entrada = request.get_json()
        analise_req = mapear_dados_entrada(dados_entrada)
        
        if not analise_req.variavelRelacionada:
            return jsonify({"erro": "A análise de correlação exige 'variavelRelacionada'."}), 400

        resultado_final = processar_request_correlacao(analise_req)
        
        if "erro" in resultado_final:
            return jsonify(resultado_final), 400
            
        return jsonify(resultado_final), 200

    except Exception as e:
        logger.error("Erro na rota /correlacao: %s", e)
        return jsonify({"erro": f"Falha interna: {e}"}), 500


@ai_bp.route("/comparar", methods=["POST"])
def comparar():
    """Rota para análise de Comparação."""
    try:
        dados_entrada = request.get_json()
        analise_req = mapear_dados_entrada(dados_entrada)

        if not analise_req.dataIncio:
             return jsonify({"erro": "Data de início é obrigatória."}), 400

        resultado_final = processar_request_comparacao(analise_req)
        
        if "erro" in resultado_final:
            return jsonify(resultado_final), 400
            
        logger.info("Análise de comparação processada com sucesso.")
        return jsonify(resultado_final), 200

    except Exception as e:
        logger.error("Erro inesperado na rota /comparar: %s", e)
        return jsonify({"erro": f"Falha no processamento: {e}"}), 500


@ai_bp.route("/previsao", methods=["POST"])
def previsao():
    """
    Rota refatorada para Análise de Previsão.
    O Controller apenas recebe, formata e delega.
    """
    try:
        dados_entrada = request.get_json()
        
        analise_req = mapear_dados_entrada(dados_entrada)

        if not analise_req.dataPrevisao:
            return jsonify({"erro": "A análise de previsão exige 'dataPrevisao'."}), 400

        resultado_final = processar_request_previsao(analise_req)
        
        if "erro" in resultado_final:
            return jsonify(resultado_final), 400
            
        return jsonify(resultado_final), 200

    except Exception as e:
        logger.error("Erro inesperado na rota /previsao: %s", e)
        return jsonify({"erro": f"Falha no processamento da requisição: {e}"}), 500