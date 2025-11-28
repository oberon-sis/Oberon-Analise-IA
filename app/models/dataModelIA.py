# Em algum arquivo de 'model/' ou 'services/'
from typing import Optional, Any
from dataclasses import dataclass

@dataclass
class IARequest:
    """Estrutura do JSON COMUM que virá no fetch."""
    pergunta: str