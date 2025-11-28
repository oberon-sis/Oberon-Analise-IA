# app/init.py (Código Atualizado)

from flask import Flask
import logging 

logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    
    logger.info('Started')
    
    from .routes.routes_analisis import ai_bp
    app.register_blueprint(ai_bp, url_prefix="/ai")

    return app