# ui/widgets/folder_selector_widget.py
"""
Widget reutilizable para selección de carpeta.
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton, QFileDialog
from PySide6.QtCore import Signal
from .base_widget import BaseWidget


class FolderSelectorWidget(BaseWidget):
    """
    Widget para seleccionar carpeta con botón de exploración.
    
    Signals:
        folder_changed: Emitido cuando cambia la carpeta (str)
    """
    
    folder_changed = Signal(str)
    
    def __init__(self, placeholder: str = "Selecciona carpeta...", 
                 button_text: str = "📂 Seleccionar", parent=None):
        """
        Args:
            placeholder: Texto placeholder del campo
            button_text: Texto del botón
            parent: Widget padre
        """
        self.placeholder = placeholder
        self.button_text = button_text
        super().__init__(parent)
    
    def _setup_ui(self):
        """Construye la interfaz del selector"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Campo de texto para mostrar ruta
        self.folder_input = QLineEdit()
        self.folder_input.setPlaceholderText(self.placeholder)
        self.folder_input.textChanged.connect(self._on_text_changed)
        
        # Botón para abrir explorador
        self.browse_btn = QPushButton(self.button_text)
        self.browse_btn.clicked.connect(self._select_folder)
        self.browse_btn.setMinimumWidth(150)
        
        layout.addWidget(self.folder_input, stretch=1)
        layout.addWidget(self.browse_btn)
    
    def _select_folder(self):
        """Abre diálogo de selección de carpeta"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Seleccionar Carpeta",
            self.folder_input.text() or "",
            QFileDialog.Option.ShowDirsOnly
        )
        
        if folder:
            self.folder_input.setText(folder)
    
    def _on_text_changed(self, text: str):
        """Emite señal cuando cambia el texto"""
        self.folder_changed.emit(text)
    
    def get_folder(self) -> str:
        """
        Obtiene la ruta de carpeta seleccionada.
        
        Returns:
            str: Ruta de la carpeta o cadena vacía
        """
        return self.folder_input.text().strip()
    
    def set_folder(self, folder_path: str):
        """
        Establece la ruta de carpeta programáticamente.
        
        Args:
            folder_path: Ruta de la carpeta
        """
        self.folder_input.setText(folder_path)
    
    def clear(self):
        """Limpia el campo de carpeta"""
        self.folder_input.clear()