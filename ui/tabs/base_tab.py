# ui/tabs/base_tab.py
"""
Tab base con integración de temas, logging y utilidades comunes.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Signal


class BaseTab(QWidget):
    """
    Widget base para tabs de la aplicación.
    
    Características:
    - Integración automática con ThemeManager
    - Logger específico por tab (usando MatrixLogger)
    - Señales comunes para comunicación con ventana principal
    - Métodos helpers para acceso a temas
    
    Signals:
        error_occurred: Emitido cuando hay error (str)
        status_changed: Emitido cuando cambia el estado (str)
    """
    
    # Señales comunes
    error_occurred = Signal(str)
    status_changed = Signal(str)
    
    def __init__(self, tab_name: str, parent=None):
        """
        Args:
            tab_name: Nombre del tab para logging
            parent: Widget padre
        """
        super().__init__(parent)
        
        self.tab_name = tab_name
        
        # Importar aquí para evitar imports circulares
        from ui.theme_manager import ThemeManager
        from utils.logger import MatrixLogger
        
        self.theme_manager = ThemeManager()
        self.logger = MatrixLogger(tab_name)
        
        self._setup_base_layout()
        self._setup_ui()
        self._connect_signals()
        self._apply_theme()
    
    def _setup_base_layout(self):
        """Configura layout base del tab"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)
    
    def _setup_ui(self):
        """
        Método abstracto para construir UI del tab.
        DEBE ser implementado por subclases.
        """
        raise NotImplementedError(
            f"La subclase {self.__class__.__name__} debe implementar _setup_ui()"
        )
    
    def _connect_signals(self):
        """
        Método para conectar señales específicas del tab.
        Puede ser sobrescrito por subclases si necesitan conectar señales.
        """
        pass
    
    def _apply_theme(self):
        """
        Aplica tema actual al tab.
        Los estilos se heredan automáticamente de QApplication.
        Este método puede ser sobrescrito para estilos específicos del tab.
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
        return self.theme_manager.get_color(color_key)
    
    def get_theme_spacing(self, spacing_key: str) -> int:
        """
        Helper para obtener espaciados del tema actual.
        
        Args:
            spacing_key: Clave del espaciado (ej: 'padding_medium')
            
        Returns:
            int: Valor del espaciado en píxeles
        """
        return self.theme_manager.get_spacing(spacing_key)
    
    def show_error(self, message: str):
        """
        Muestra error, lo registra en log y emite señal.
        
        Args:
            message: Mensaje de error
        """
        self.logger.error(message)
        self.error_occurred.emit(message)
    
    def show_status(self, message: str):
        """
        Actualiza estado, lo registra en log y emite señal.
        
        Args:
            message: Mensaje de estado
        """
        self.logger.info(message)
        self.status_changed.emit(message)
    
    def log_info(self, message: str):
        """
        Registra mensaje informativo.
        
        Args:
            message: Mensaje a registrar
        """
        self.logger.info(message)
    
    def log_success(self, message: str):
        """
        Registra mensaje de éxito.
        
        Args:
            message: Mensaje de éxito
        """
        self.logger.success(message)
    
    def log_warning(self, message: str):
        """
        Registra advertencia.
        
        Args:
            message: Mensaje de advertencia
        """
        self.logger.warning(message)