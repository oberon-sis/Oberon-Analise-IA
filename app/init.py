# app/init.py (Código Atualizado)

from flask import Flask
from .config import load_env
import logging # NOVO IMPORT

def create_app():
    app = Flask(__name__)
    load_env(app)

    logging.basicConfig(
        level=logging.INFO, 
        format='[%(asctime)s] %(levelname)s in %(module)s.%(funcName)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    from .routes.routes_analisis import ai_bp
    app.register_blueprint(ai_bp, url_prefix="/ai")

    return app