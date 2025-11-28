from app.init import create_app
from logging_config import setup_logging
import logging

setup_logging()
logger = logging.getLogger(__name__)

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5055, debug=True)
