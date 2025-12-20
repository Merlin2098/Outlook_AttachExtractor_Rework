# ui/widgets/phrase_search_widget.py
"""
Widget para búsqueda por frases con selector de modo y opción de habilitar/deshabilitar.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
    QComboBox, QLabel, QCheckBox, QSizePolicy
)
from PySide6.QtCore import Signal
from ui.widgets.base_widget import BaseWidget


class PhraseSearchWidget(BaseWidget):
    """
    Widget para ingresar frases de búsqueda y seleccionar modo de coincidencia.
    
    Modos de búsqueda:
    - all_words: Todas las palabras deben estar presentes
    - any_word: Al menos una palabra debe estar presente
    - exact_phrase: La frase exacta debe estar presente
    
    Signals:
        filter_enabled_changed(bool): Se emite cuando cambia el estado del filtro
    """
    
    filter_enabled_changed = Signal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def _setup_ui(self):
        """Construye la interfaz de búsqueda por frases"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # === CHECKBOX PARA HABILITAR/DESHABILITAR FILTRO ===
        self.enable_filter_checkbox = QCheckBox("Habilitar filtro por frases")
        self.enable_filter_checkbox.setChecked(True)  # Habilitado por defecto
        self.enable_filter_checkbox.toggled.connect(self._on_filter_toggled)
        
        # === SELECTOR DE MODO ===
        mode_layout = QHBoxLayout()
        mode_layout.setSpacing(8)
        
        mode_label = QLabel("Modo de búsqueda:")
        mode_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        
        self.mode_combo = QComboBox()
        self.mode_combo.addItems([
            "Todas las palabras",
            "Alguna palabra",
            "Frase exacta"
        ])
        self.mode_combo.setCurrentIndex(0)  # Default: todas las palabras
        self.mode_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.mode_combo, stretch=1)
        
        # === ÁREA DE TEXTO PARA FRASES ===
        self.phrases_text = QTextEdit()
        self.phrases_text.setPlaceholderText(
            "Ingresa frases a buscar (una por línea)...\n"
            "\n"
            "Ejemplo:\n"
            "  contrato firmado\n"
            "  carta de aprobación\n"
            "  documento adjunto"
        )
        self.phrases_text.setMinimumHeight(80)
        self.phrases_text.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.phrases_text.setAcceptRichText(False)  # Solo texto plano
        
        # === ENSAMBLAR LAYOUT ===
        layout.addWidget(self.enable_filter_checkbox)
        layout.addLayout(mode_layout)
        layout.addWidget(self.phrases_text, stretch=1)
    
    def _on_filter_toggled(self, enabled: bool):
        """
        Handler cuando se cambia el estado del checkbox.
        
        Args:
            enabled: True si está habilitado, False si está deshabilitado
        """
        # Habilitar/deshabilitar controles
        self.mode_combo.setEnabled(enabled)
        self.phrases_text.setEnabled(enabled)
        
        # Emitir señal
        self.filter_enabled_changed.emit(enabled)
    
    def is_filter_enabled(self) -> bool:
        """
        Verifica si el filtro está habilitado.
        
        Returns:
            bool: True si el filtro está habilitado
        """
        return self.enable_filter_checkbox.isChecked()
    
    def get_phrases(self) -> list:
        """
        Obtiene lista de frases ingresadas (limpias y normalizadas).
        
        Si el filtro está deshabilitado, retorna lista vacía.
        
        Returns:
            list[str]: Lista de frases, una por línea (vacía si filtro deshabilitado)
        """
        # Si el filtro está deshabilitado, retornar lista vacía
        if not self.is_filter_enabled():
            return []
        
        text = self.phrases_text.toPlainText().strip()
        
        if not text:
            return []
        
        # Dividir por líneas y limpiar espacios
        phrases = [
            line.strip()
            for line in text.split('\n')
            if line.strip()  # Ignorar líneas vacías
        ]
        
        return phrases
    
    def get_search_mode(self) -> str:
        """
        Obtiene el modo de búsqueda seleccionado.
        
        Returns:
            str: 'all_words', 'any_word', o 'exact_phrase'
        """
        mode_mapping = {
            0: "all_words",      # Todas las palabras
            1: "any_word",       # Alguna palabra
            2: "exact_phrase"    # Frase exacta
        }
        
        index = self.mode_combo.currentIndex()
        return mode_mapping.get(index, "all_words")
    
    def set_phrases(self, phrases: list):
        """
        Establece las frases programáticamente.
        
        Args:
            phrases: Lista de frases (strings)
        """
        if not phrases:
            self.phrases_text.clear()
            return
        
        text = '\n'.join(phrases)
        self.phrases_text.setPlainText(text)
    
    def set_search_mode(self, mode: str):
        """
        Establece el modo de búsqueda programáticamente.
        
        Args:
            mode: 'all_words', 'any_word', o 'exact_phrase'
        """
        mode_index_mapping = {
            "all_words": 0,
            "any_word": 1,
            "exact_phrase": 2
        }
        
        index = mode_index_mapping.get(mode, 0)
        self.mode_combo.setCurrentIndex(index)
    
    def set_filter_enabled(self, enabled: bool):
        """
        Habilita o deshabilita el filtro programáticamente.
        
        Args:
            enabled: True para habilitar, False para deshabilitar
        """
        self.enable_filter_checkbox.setChecked(enabled)
    
    def clear(self):
        """Limpia el widget"""
        self.phrases_text.clear()
        self.mode_combo.setCurrentIndex(0)
        self.enable_filter_checkbox.setChecked(True)  # Resetear a habilitado
    
    def is_empty(self) -> bool:
        """
        Verifica si no hay frases ingresadas O si el filtro está deshabilitado.
        
        Returns:
            bool: True si está vacío o deshabilitado
        """
        if not self.is_filter_enabled():
            return True
        
        return len(self.get_phrases()) == 0