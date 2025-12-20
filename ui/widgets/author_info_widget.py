# ui/widgets/author_info_widget.py
"""
Widget de información del autor para el header de la aplicación.
"""

from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt


class AuthorInfoWidget(QLabel):
    """
    Label con información del autor y fecha.
    
    Muestra: "@Diciembre 2025 | Autor: Ricardo Fabian Uculmana Quispe"
    
    Características:
    - Texto semi-transparente que se adapta a ambos temas
    - Alineación izquierda
    - Estilo minimalista y profesional
    """
    
    def __init__(self, parent=None):
        """
        Inicializa el widget de información del autor.
        
        Args:
            parent: Widget padre
        """
        super().__init__(parent)
        
        # Establecer texto
        self.setText("@Diciembre 2025 | Autor: Ricardo Fabian Uculmana Quispe")
        
        # Configuración de alineación
        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        # Hacer que el texto no sea seleccionable
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        
        # Estilo inicial (será actualizado por update_theme)
        self._is_dark = True  # Default
    
    def update_theme(self, is_dark: bool):
        """
        Actualiza el estilo según el tema activo.
        
        Args:
            is_dark: True si es tema oscuro, False si es claro
        """
        self._is_dark = is_dark
        
        if is_dark:
            # Tema oscuro: usar mismo color que títulos de sección (#38BDF8 - primary)
            color = "#38BDF8"
        else:
            # Tema claro: texto oscuro con semi-transparencia
            color = "rgba(30, 41, 59, 0.6)"  # Gris oscuro (#1E293B con alpha)
        
        self.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 13px;
                font-weight: normal;
                padding: 5px 10px;
                background-color: transparent;
            }}
        """)


# Exportar
__all__ = ['AuthorInfoWidget']