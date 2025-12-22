# ui/widgets/__init__.py
"""
Módulo de widgets reutilizables para OutlookExtractor.
Exporta todos los widgets disponibles.
"""

from .base_widget import BaseWidget
from .folder_selector_widget import FolderSelectorWidget
from .date_range_widget import DateRangeWidget
from .phrase_search_widget import PhraseSearchWidget
from .progress_widget import ProgressWidget
from .outlook_folder_selector import OutlookFolderSelector
from .theme_toggle_widget import ThemeToggleWidget
from .author_info_widget import AuthorInfoWidget

__all__ = [
    'BaseWidget',
    'FolderSelectorWidget',
    'DateRangeWidget',
    'PhraseSearchWidget',
    'ProgressWidget',
    'OutlookFolderSelector',
    'ThemeToggleWidget',
    'AuthorInfoWidget'
]