import google.generativeai as genai
from dotenv import load_dotenv
import os
import logging

logger = logging.getLogger(__name__)

load_dotenv()

def get_gemini_response(prompt: str, response_schema: dict = None) -> str:
    """
    Gera conteúdo usando a API Gemini. Pode solicitar resposta JSON estruturada.
    """
    api_key = os.getenv("GEMINI_API_KEY") 
    
    if not api_key:
        logger.error("Chave GEMINI_API_KEY não encontrada no ambiente.")
        raise Exception("Chave GEMINI_API_KEY não configurada.")
        
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    generation_config = {}
    if response_schema:
        generation_config = {
            "response_mime_type": "application/json",
            "response_schema": response_schema
        }
    
    try:
        response = model.generate_content(
            prompt, 
            generation_config=generation_config 
        )
        
        return response.text
        
    except Exception as e:
        logger.error("Erro na chamada da API Gemini: %s", e)
        raise Exception(f"Falha na API Gemini: {e}")