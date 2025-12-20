# ui/widgets/phrase_search_widget.py
"""
Widget para búsqueda por frases con selector de modo y opción de habilitar/deshabilitar.
"""

import re
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
    QComboBox, QLabel, QCheckBox, QSizePolicy
)
from PySide6.QtCore import Signal
from ui.widgets.base_widget import BaseWidget


class PhraseSearchWidget(BaseWidget):
    """
    Widget para ingresar frases de búsqueda y seleccionar modo de coincidencia.
    
    Delimitadores soportados:
    - Pipe (|): Separador principal de frases
    - Comillas (""): Para incluir pipes literales dentro de una frase
    
    Ejemplos:
        "contrato | documento | carta" → ["contrato", "documento", "carta"]
        '"Reporte Q1 | Aprobado" | documento' → ["Reporte Q1 | Aprobado", "documento"]
    
    Modos de búsqueda:
    - all_words: Todas las palabras deben estar presentes
    - any_word: Al menos una palabra debe estar presente
    - exact_phrase: La frase exacta debe estar presente
    
    Signals:
        filter_enabled_changed(bool): Se emite cuando cambia el estado del filtro
        phrases_changed(): Se emite cuando cambian las frases ingresadas
    """
    
    filter_enabled_changed = Signal(bool)
    phrases_changed = Signal()
    
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
            'Ingresa frases separadas por "|" ...\n'
            '\n'
            'Ejemplos básicos:\n'
            '  contrato | documento | carta\n'
            '  factura aprobada | orden de compra | cotización\n'
            '\n'
            'Si el texto contiene "|", usa comillas:\n'
            '  "Reporte Q1 | Aprobado" | documento normal\n'
            '  "Plan A | B | C" | carta | "Opción X | Y"\n'
            '\n'
            'Consejos:\n'
            '  • Separa frases con "|" (pipe)\n'
            '  • Usa comillas "" si la frase contiene "|"\n'
            '  • Los espacios extras se eliminan automáticamente'
        )
        self.phrases_text.setMinimumHeight(80)
        self.phrases_text.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.phrases_text.setAcceptRichText(False)  # Solo texto plano
        
        # Conectar señal de cambio de texto
        self.phrases_text.textChanged.connect(self._on_text_changed)
        
        # === LABEL DE VALIDACIÓN (opcional) ===
        self.validation_label = QLabel("")
        self.validation_label.setStyleSheet("color: #ff9800; font-size: 11px;")
        self.validation_label.setWordWrap(True)
        self.validation_label.hide()
        
        # === ENSAMBLAR LAYOUT ===
        layout.addWidget(self.enable_filter_checkbox)
        layout.addLayout(mode_layout)
        layout.addWidget(self.phrases_text, stretch=1)
        layout.addWidget(self.validation_label)
    
    def _on_filter_toggled(self, enabled: bool):
        """
        Handler cuando se cambia el estado del checkbox.
        
        Args:
            enabled: True si está habilitado, False si está deshabilitado
        """
        # Habilitar/deshabilitar controles
        self.mode_combo.setEnabled(enabled)
        self.phrases_text.setEnabled(enabled)
        
        # Ocultar validación si se deshabilita
        if not enabled:
            self.validation_label.hide()
        
        # Emitir señal
        self.filter_enabled_changed.emit(enabled)
    
    def _on_text_changed(self):
        """Handler cuando cambia el texto (para validación en tiempo real)"""
        # Validar comillas sin cerrar
        text = self.phrases_text.toPlainText()
        quote_count = text.count('"')
        
        if quote_count % 2 != 0:
            self.validation_label.setText("⚠️ Advertencia: Hay una comilla sin cerrar")
            self.validation_label.show()
        else:
            self.validation_label.hide()
        
        # Emitir señal de cambio
        self.phrases_changed.emit()
    
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
        
        Soporta dos formatos:
        1. Separación por pipe (|): "frase1 | frase2 | frase3"
        2. Escape con comillas: '"frase con | pipe" | frase normal'
        
        Si el filtro está deshabilitado, retorna lista vacía.
        
        Returns:
            list[str]: Lista de frases procesadas
        """
        # Si el filtro está deshabilitado, retornar lista vacía
        if not self.is_filter_enabled():
            return []
        
        text = self.phrases_text.toPlainText().strip()
        
        if not text:
            return []
        
        phrases = []
        
        # Regex para capturar texto entre comillas O texto sin comillas separado por |
        # Patrón: "texto entre comillas" | texto sin comillas
        # Grupos: (1) texto entre comillas, (2) texto sin comillas
        pattern = r'"([^"]*)"|([^|]+)'
        
        matches = re.findall(pattern, text)
        
        for quoted, unquoted in matches:
            if quoted is not None and quoted != "":
                # Texto entre comillas (puede contener pipes)
                phrase = quoted.strip()
                if phrase:
                    phrases.append(phrase)
            elif unquoted:
                # Texto sin comillas
                phrase = unquoted.strip()
                if phrase:
                    phrases.append(phrase)
        
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
        
        # Unir con pipe como delimitador
        text = ' | '.join(phrases)
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
        self.validation_label.hide()
    
    def is_empty(self) -> bool:
        """
        Verifica si no hay frases ingresadas O si el filtro está deshabilitado.
        
        Returns:
            bool: True si está vacío o deshabilitado
        """
        if not self.is_filter_enabled():
            return True
        
        return len(self.get_phrases()) == 0
    
    def get_phrase_count(self) -> int:
        """
        Retorna el número de frases procesadas.
        
        Returns:
            int: Cantidad de frases
        """
        return len(self.get_phrases())
    
    def has_unclosed_quotes(self) -> bool:
        """
        Verifica si hay comillas sin cerrar.
        
        Returns:
            bool: True si hay comillas desemparejadas
        """
        text = self.phrases_text.toPlainText()
        return text.count('"') % 2 != 0