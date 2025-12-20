# ui/widgets/theme_toggle_widget.py
"""
Widget de toggle para cambiar entre tema claro y oscuro.
"""

from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Signal, Qt


class ThemeToggleWidget(QPushButton):
    """
    Botón toggle para alternar entre tema claro y oscuro.
    
    Estados visuales:
    - ☀️ (Sol): Tema claro activo → Click cambia a oscuro
    - 🌙 (Luna): Tema oscuro activo → Click cambia a claro
    
    Signals:
        theme_changed(str): Emitido al cambiar tema ('light' o 'dark')
    """
    
    theme_changed = Signal(str)
    
    def __init__(self, initial_theme: str = "dark", parent=None):
        """
        Inicializa el widget de toggle.
        
        Args:
            initial_theme: Tema inicial ('light' o 'dark')
            parent: Widget padre
        """
        super().__init__(parent)
        
        self.current_theme = initial_theme
        
        # Configuración visual del botón - MÁS GRANDE Y VISIBLE
        self.setFixedSize(80, 45)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Aplicar estilos mejorados
        self.setStyleSheet("""
            QPushButton {
                font-size: 28px;
                border: 2px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                background-color: rgba(0, 0, 0, 0.1);
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.15);
                border: 2px solid rgba(255, 255, 255, 0.3);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.25);
            }
        """)
        
        # Actualizar apariencia inicial
        self._update_appearance()
        
        # Conectar señal de click
        self.clicked.connect(self._toggle_theme)
    
    def _toggle_theme(self):
        """Alterna entre tema claro y oscuro"""
        if self.current_theme == "dark":
            self.set_theme("light")
        else:
            self.set_theme("dark")
    
    def set_theme(self, theme: str):
        """
        Establece el tema actual.
        
        Args:
            theme: 'light' o 'dark'
        """
        if theme not in ['light', 'dark']:
            return
        
        self.current_theme = theme
        self._update_appearance()
        self.theme_changed.emit(theme)
    
    def _update_appearance(self):
        """Actualiza el icono y tooltip según el tema actual"""
        if self.current_theme == "dark":
            # Tema oscuro activo → Mostrar luna
            self.setText("🌙")
            self.setToolTip("Tema oscuro activo\nClick para cambiar a tema claro")
        else:
            # Tema claro activo → Mostrar sol
            self.setText("☀️")
            self.setToolTip("Tema claro activo\nClick para cambiar a tema oscuro")
    
    def get_current_theme(self) -> str:
        """
        Obtiene el tema actual.
        
        Returns:
            str: 'light' o 'dark'
        """
        return self.current_theme


# Exportar
__all__ = ['ThemeToggleWidget']