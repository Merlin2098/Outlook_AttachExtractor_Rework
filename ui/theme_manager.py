# ui/theme_manager.py
"""
Gestor de temas para MatrixMAE.
Lee configuraciones de theme_light.json y theme_dark.json.
"""

import json
from pathlib import Path
from typing import Dict, Any


class ThemeManager:
    """
    Gestiona la carga y aplicación de temas visuales.
    
    Características:
    - Carga temas desde theme_light.json y theme_dark.json
    - Genera stylesheets QSS completos
    - Persiste selección de tema usando ConfigManager
    - Tema por defecto: 'light'
    """
    
    def __init__(self, config_dir: Path = None, config_manager=None):
        """
        Inicializa el gestor de temas.
        
        Args:
            config_dir: Directorio de configuración (por defecto: ./config)
            config_manager: Instancia de ConfigManager (opcional)
        """
        if config_dir is None:
            # Detectar directorio base
            import sys
            if getattr(sys, 'frozen', False):
                base_dir = Path(sys._MEIPASS)
            else:
                base_dir = Path(__file__).parent.parent
            config_dir = base_dir / "config"
        
        self.config_dir = Path(config_dir)
        self.themes_cache = {}
        
        # Usar ConfigManager para persistencia
        if config_manager is None:
            from config.config_manager import ConfigManager
            config_manager = ConfigManager()
        self.config_manager = config_manager
        
        # Cargar tema guardado o usar default (LIGHT)
        self._current_theme_name = self._load_saved_theme()
        self._current_theme_data = self._load_theme_file(self._current_theme_name)
    
    def _load_saved_theme(self) -> str:
        """
        Carga el tema guardado desde config usando ConfigManager.
        
        Returns:
            str: Nombre del tema ('light' o 'dark'), default 'light'
        """
        return self.config_manager.get_tema()
    
    def _save_theme(self, theme_name: str):
        """
        Guarda el tema seleccionado usando ConfigManager.
        
        Args:
            theme_name: Nombre del tema a guardar
        """
        self.config_manager.set_tema(theme_name)
    
    def _load_theme_file(self, theme_name: str) -> Dict[str, Any]:
        """
        Carga un archivo de tema específico.
        
        Args:
            theme_name: 'light' o 'dark'
            
        Returns:
            Dict con configuración del tema
        """
        # Usar caché si está disponible
        if theme_name in self.themes_cache:
            return self.themes_cache[theme_name]
        
        theme_file = self.config_dir / f"theme_{theme_name}.json"
        
        if not theme_file.exists():
            print(f"⚠️ Archivo de tema no encontrado: {theme_file}")
            print(f"   Usando tema por defecto")
            # Fallback a tema básico
            return self._get_fallback_theme()
        
        try:
            with open(theme_file, 'r', encoding='utf-8') as f:
                theme_data = json.load(f)
            
            # Cachear
            self.themes_cache[theme_name] = theme_data
            
            print(f"✅ Tema cargado: {theme_file}")
            return theme_data
        
        except Exception as e:
            print(f"❌ Error cargando tema: {e}")
            return self._get_fallback_theme()
    
    def _get_fallback_theme(self) -> Dict[str, Any]:
        """
        Retorna un tema básico de emergencia (LIGHT).
        
        Returns:
            Dict con configuración mínima
        """
        return {
            "name": "fallback",
            "colors": {
                "primary": "#0284C7",
                "background": "#FFFFFF",
                "text": {"primary": "#1E293B"}
            },
            "pyqt5": {
                "stylesheet": """
                    QWidget { 
                        background-color: #FFFFFF; 
                        color: #1E293B; 
                    }
                    QPushButton {
                        background-color: #0284C7;
                        color: #FFFFFF;
                        border-radius: 4px;
                        padding: 8px 16px;
                    }
                """
            }
        }
    
    def get_stylesheet(self) -> str:
        """
        Obtiene el stylesheet QSS completo del tema actual.
        
        Returns:
            str: Stylesheet QSS listo para aplicar
        """
        try:
            stylesheet = self._current_theme_data.get("pyqt5", {}).get("stylesheet", "")
            
            # Agregar estilos adicionales para QDateEdit si no están
            if "QDateEdit" not in stylesheet:
                stylesheet += self._get_dateedit_styles()
            
            return stylesheet
        
        except Exception as e:
            print(f"❌ Error obteniendo stylesheet: {e}")
            return ""
    
    def _get_dateedit_styles(self) -> str:
        """
        Genera estilos específicos para QDateEdit según el tema actual.
        
        Returns:
            str: CSS para QDateEdit
        """
        is_dark = self._current_theme_name == 'dark'
        
        if is_dark:
            # Tema oscuro
            return """
/* ========== DATE EDIT ========== */
QDateEdit {
    background-color: #1E293B;
    border: 2px solid #334155;
    border-radius: 4px;
    padding: 8px 12px;
    color: #E2E8F0;
    min-width: 130px;
}

QDateEdit:focus {
    border-color: #38BDF8;
}

QDateEdit:disabled {
    background-color: #2C3549;
    color: #64748B;
}

QDateEdit::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: center right;
    width: 25px;
    border-left: 2px solid #334155;
    border-top-right-radius: 4px;
    border-bottom-right-radius: 4px;
}

QDateEdit::down-arrow {
    width: 0;
    height: 0;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #38BDF8;
}

QCalendarWidget {
    background-color: #1B2233;
    border: 1px solid #2C3549;
    border-radius: 8px;
}

QCalendarWidget QToolButton {
    color: #E2E8F0;
    background-color: transparent;
    border-radius: 4px;
    padding: 5px;
}

QCalendarWidget QToolButton:hover {
    background-color: #38BDF8;
    color: #FFFFFF;
}

QCalendarWidget QAbstractItemView {
    selection-background-color: #38BDF8;
    selection-color: #FFFFFF;
    background-color: #1B2233;
    color: #E2E8F0;
}

QCalendarWidget QWidget {
    color: #E2E8F0;
}
"""
        else:
            # Tema claro
            return """
/* ========== DATE EDIT ========== */
QDateEdit {
    background-color: #FFFFFF;
    border: 2px solid #CBD5E1;
    border-radius: 4px;
    padding: 8px 12px;
    color: #1E293B;
    min-width: 130px;
}

QDateEdit:focus {
    border-color: #0284C7;
}

QDateEdit:disabled {
    background-color: #F1F5F9;
    color: #64748B;
}

QDateEdit::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: center right;
    width: 25px;
    border-left: 2px solid #CBD5E1;
    border-top-right-radius: 4px;
    border-bottom-right-radius: 4px;
}

QDateEdit::down-arrow {
    width: 0;
    height: 0;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #0284C7;
}

QCalendarWidget {
    background-color: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
}

QCalendarWidget QToolButton {
    color: #1E293B;
    background-color: transparent;
    border-radius: 4px;
    padding: 5px;
}

QCalendarWidget QToolButton:hover {
    background-color: #0284C7;
    color: #FFFFFF;
}

QCalendarWidget QAbstractItemView {
    selection-background-color: #0284C7;
    selection-color: #FFFFFF;
    background-color: #FFFFFF;
    color: #1E293B;
}

QCalendarWidget QWidget {
    color: #1E293B;
}
"""
    
    def set_theme(self, theme_name: str):
        """
        Cambia el tema actual y lo guarda.
        
        Args:
            theme_name: 'light' o 'dark'
        """
        if theme_name not in ['light', 'dark']:
            print(f"⚠️ Tema inválido: {theme_name}")
            return
        
        self._current_theme_name = theme_name
        self._current_theme_data = self._load_theme_file(theme_name)
        self._save_theme(theme_name)
        
        print(f"✅ Tema cambiado a: {theme_name}")
    
    def get_current_theme(self) -> str:
        """
        Obtiene el nombre del tema actual.
        
        Returns:
            str: 'light' o 'dark'
        """
        return self._current_theme_name
    
    def get_color(self, color_key: str) -> str:
        """
        Obtiene un color específico del tema actual.
        
        Args:
            color_key: Clave del color (ej: 'primary', 'background')
            
        Returns:
            str: Código hexadecimal del color o color por defecto
        """
        try:
            colors = self._current_theme_data.get("colors", {})
            
            # Manejar colores anidados (ej: text.primary)
            if '.' in color_key:
                parts = color_key.split('.')
                value = colors
                for part in parts:
                    value = value.get(part, {})
                return value if isinstance(value, str) else "#000000"
            
            return colors.get(color_key, "#000000")
        
        except Exception as e:
            print(f"⚠️ Error obteniendo color '{color_key}': {e}")
            return "#000000"
    
    def get_spacing(self, spacing_key: str) -> int:
        """
        Obtiene un valor de espaciado del tema.
        
        Args:
            spacing_key: Clave del espaciado
            
        Returns:
            int: Valor en píxeles o 0
        """
        try:
            spacing = self._current_theme_data.get("spacing", {})
            return spacing.get(spacing_key, 0)
        except:
            return 0


# Exportar
__all__ = ['ThemeManager']