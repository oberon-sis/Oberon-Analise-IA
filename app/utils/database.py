# app/utils/database.py (Código Atualizado)

import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
import logging 

logger = logging.getLogger(__name__)

load_dotenv() 

def fazer_consulta_banco(config):
    """
    Função de utilidade que centraliza a execução de consultas SQL, 
    incluindo CALL de Stored Procedures. Gerencia a conexão e o cursor internamente.

    config (dict): Deve conter:
        - "query" (str): A instrução SQL ou CALL da Stored Procedure.
        - "params" (tuple/list, opcional): Os parâmetros para a instrução SQL.
    
    Retorna: Lista de tuplas do resultado (ou lastrowid/rowcount para comandos DML).
    Lança RuntimeError em caso de falha.
    """
    instrucao_sql = config.get("query")
    valores = config.get("params", None)

    db_config = {
        'user': os.getenv("USER_DB"),
        'password': os.getenv("PASSWORD_DB"),
        'host': os.getenv("HOST_DB"),
        'database': os.getenv("DATABASE_DB")
    }
    
    conn = None
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Execução da Query
        if valores:
            cursor.execute(instrucao_sql, valores if isinstance(valores, (tuple, list)) else (valores,))
        else:
            cursor.execute(instrucao_sql)

        sql_tipo = instrucao_sql.strip().lower()
        
        # ... (lógica de SELECT/CALL/INSERT/UPDATE/DELETE inalterada) ...
        if sql_tipo.startswith("select") or sql_tipo.startswith("call"):
            resultado = cursor.fetchall()
            
            if sql_tipo.startswith("call"):
                while cursor.nextset():
                    pass 
            
            return resultado
        else:
            conn.commit()
            
            if sql_tipo.startswith("insert"):
                return cursor.lastrowid
            else:
                return cursor.rowcount

    except Error as e:
        error_message = f"Erro no MySQL: {e}"
        # logger.error em vez de print
        logger.error(error_message) 
        raise RuntimeError(error_message)
    except Exception as e:
        error_message = f"Erro ao executar consulta: {e}"
        # logger.error em vez de print
        logger.error(error_message)
        raise RuntimeError(error_message)
    finally:
        if conn and conn.is_connected():
            conn.close()