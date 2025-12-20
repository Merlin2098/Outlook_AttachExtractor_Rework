# ui/tabs/__init__.py
"""
Módulo de tabs para MatrixMAE.
Exporta todos los tabs disponibles.
"""

from .base_tab import BaseTab
from .tab_extractor import TabExtractor
from .tab_clasificador import TabClasificador

__all__ = [
    'BaseTab',
    'TabExtractor',
    'TabClasificador'
]