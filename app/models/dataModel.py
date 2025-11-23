# Em algum arquivo de 'model/' ou 'services/'
from typing import Optional, Any
from dataclasses import dataclass

@dataclass
class AnaliseRequest:
    """Estrutura do JSON COMUM que virá no fetch."""
    tipoAnalise: str
    dataIncio: str
    metricaAnalisar: str
    fkEmpresa: int
    fkMaquina: Optional[int] = None
    dataPrevisao: Optional[str] = None  # Necessário apenas para 'previsao'
    componente: Optional[str] = None     # Opcional em todos os tipos
    variavelRelacionada: Optional[str] = None # Necessário apenas para 'correlacao'