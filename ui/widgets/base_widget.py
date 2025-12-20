# ui/widgets/base_widget.py
"""
Widget base con soporte automático de temas.
Todos los widgets heredan de esta clase.
"""

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Signal


class BaseWidget(QWidget):
    """
    Widget base con integración automática de temas.
    
    Características:
    - Auto-aplicación de estilos vía ThemeManager
    - Señales comunes para manejo de errores
    - Métodos helpers para acceso a colores/espaciados
    
    Signals:
        error_occurred: Emite mensaje de error (str)
    """
    
    # Señales comunes
    error_occurred = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._apply_theme()
    
    def _setup_ui(self):
        """
        Método abstracto para que subclases implementen su UI.
        Sobrescribir en widgets hijos.
        """
        pass
    
    def _apply_theme(self):
        """
        Aplica el tema actual al widget.
        Los estilos se heredan de QApplication por defecto.
        Este método puede ser sobrescrito para estilos específicos.
        """
        pass
    
    def get_theme_color(self, color_key: str) -> str:
        """
        Helper para obtener colores del tema actual.
        
        Args:
            color_key: Clave del color (ej: 'primary', 'background')
            
        Returns:
            str: Código hexadecimal del color
        """
        from ui.theme_manager import ThemeManager
        theme_manager = ThemeManager()
        return theme_manager.get_color(color_key)
    
    def get_theme_spacing(self, spacing_key: str) -> int:
        """
        Helper para obtener espaciados del tema actual.
        
        Args:
            spacing_key: Clave del espaciado (ej: 'padding_medium')
            
        Returns:
            int: Valor del espaciado en píxeles
        """
        from ui.theme_manager import ThemeManager
        theme_manager = ThemeManager()
        return theme_manager.get_spacing(spacing_key)
    
    def show_error(self, message: str):
        """
        Emite señal de error para que la UI principal la capture.
        
        Args:
            message: Mensaje de error a mostrar
        """
        self.error_occurred.emit(message)