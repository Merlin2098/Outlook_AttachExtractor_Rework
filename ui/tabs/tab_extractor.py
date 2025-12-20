# ui/tabs/tab_extractor.py
"""
Tab completo para extracción de adjuntos de emails.
Incluye todos los controles y lógica de UI.
"""

from PySide6.QtWidgets import (
    QGroupBox, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QMessageBox, QSizePolicy
)
from PySide6.QtCore import Signal, Slot, QThreadPool
from ui.tabs.base_tab import BaseTab
from ui.widgets import (
    FolderSelectorWidget,
    DateRangeWidget,
    PhraseSearchWidget,
    ProgressWidget,
    OutlookFolderSelector
)
from workers import ExtractorWorker


class TabExtractor(BaseTab):
    """
    Tab de extracción de adjuntos de emails.
    
    Signals:
        extraction_started: Emitido al iniciar extracción (dict con parámetros)
        extraction_finished: Emitido al terminar extracción (dict con estadísticas)
        extraction_cancelled: Emitido al cancelar extracción
    """
    
    extraction_started = Signal(dict)
    extraction_finished = Signal(dict)
    extraction_cancelled = Signal()
    
    def __init__(self, parent=None):
        super().__init__("Extractor", parent)
        
        # Backend y worker
        self.backend = None
        self.worker = None
        self.threadpool = QThreadPool.globalInstance()
    
    def _setup_ui(self):
        """Construye interfaz del extractor con layout horizontal para criterios"""
        
        # Configurar spacing del layout principal
        self.main_layout.setSpacing(15)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        
        # === SECCIÓN: CARPETA DESTINO ===
        folder_group = QGroupBox("📁 Carpeta de Destino")
        folder_group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        folder_group.setMinimumHeight(90)
        folder_layout = QVBoxLayout()
        folder_layout.setSpacing(8)
        folder_layout.setContentsMargins(15, 15, 15, 15)
        
        self.folder_widget = FolderSelectorWidget(
            placeholder="Selecciona carpeta donde guardar adjuntos...",
            button_text="📂 Seleccionar Carpeta"
        )
        self.folder_widget.setMinimumHeight(40)
        
        folder_layout.addWidget(self.folder_widget)
        folder_group.setLayout(folder_layout)
        
        # === SECCIÓN: BANDEJA DE OUTLOOK ===
        outlook_group = QGroupBox("📧 Bandeja de Correo")
        outlook_group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        outlook_group.setMinimumHeight(90)
        outlook_layout = QVBoxLayout()
        outlook_layout.setSpacing(8)
        outlook_layout.setContentsMargins(15, 15, 15, 15)
        
        self.outlook_folder_widget = OutlookFolderSelector(
            placeholder="Selecciona bandeja de Outlook...",
            button_text="📧 Explorar Outlook"
        )
        self.outlook_folder_widget.setMinimumHeight(40)
        
        outlook_layout.addWidget(self.outlook_folder_widget)
        outlook_group.setLayout(outlook_layout)
        
        # === SECCIÓN: CRITERIOS DE BÚSQUEDA (LAYOUT HORIZONTAL) ===
        search_group = QGroupBox("🔍 Criterios de Búsqueda")
        search_group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        search_group.setMinimumHeight(280)
        
        # Layout HORIZONTAL principal para dividir en 2 columnas
        search_main_layout = QHBoxLayout()
        search_main_layout.setSpacing(15)
        search_main_layout.setContentsMargins(15, 15, 15, 15)
        
        # === COLUMNA IZQUIERDA: FECHAS ===
        left_column = QVBoxLayout()
        left_column.setSpacing(10)
        
        date_label = QLabel("Filtro por Fechas:")
        date_label.setProperty("class", "subtitle")
        
        self.date_range_widget = DateRangeWidget()
        self.date_range_widget.setMinimumHeight(40)
        
        left_column.addWidget(date_label)
        left_column.addWidget(self.date_range_widget)
        left_column.addStretch()
        
        # === COLUMNA DERECHA: FRASES ===
        right_column = QVBoxLayout()
        right_column.setSpacing(10)
        
        phrase_label = QLabel("Búsqueda por Frases (separar con '|'):")
        phrase_label.setProperty("class", "subtitle")
        
        self.phrase_widget = PhraseSearchWidget()
        self.phrase_widget.setMinimumHeight(150)
        
        right_column.addWidget(phrase_label)
        right_column.addWidget(self.phrase_widget, 1)
        
        # === ENSAMBLAR COLUMNAS ===
        search_main_layout.addLayout(left_column, 1)
        search_main_layout.addLayout(right_column, 1)
        
        search_group.setLayout(search_main_layout)
        
        # === SECCIÓN: PROGRESO ===
        progress_group = QGroupBox("📊 Progreso de Extracción")
        progress_group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        progress_group.setMinimumHeight(120)
        progress_group.setMaximumHeight(160)
        progress_layout = QVBoxLayout()
        progress_layout.setSpacing(8)
        progress_layout.setContentsMargins(15, 15, 15, 15)
        
        self.progress_widget = ProgressWidget(show_stats=True)
        
        progress_layout.addWidget(self.progress_widget)
        progress_group.setLayout(progress_layout)
        
        # === BOTONES DE ACCIÓN ===
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(15)
        
        self.start_btn = QPushButton("▶️ Iniciar Extracción")
        self.start_btn.setMinimumHeight(45)
        self.start_btn.clicked.connect(self._on_start_clicked)
        
        self.cancel_btn = QPushButton("⏹️ Cancelar Proceso")
        self.cancel_btn.setMinimumHeight(45)
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self._on_cancel_clicked)
        
        actions_layout.addWidget(self.start_btn)
        actions_layout.addWidget(self.cancel_btn)
        
        # === ENSAMBLAR LAYOUT PRINCIPAL ===
        self.main_layout.addWidget(folder_group, 0)
        self.main_layout.addWidget(outlook_group, 0)
        self.main_layout.addWidget(search_group, 1)
        self.main_layout.addWidget(progress_group, 0)
        self.main_layout.addLayout(actions_layout, 0)
    
    def _connect_signals(self):
        """Conecta señales internas"""
        self.folder_widget.folder_changed.connect(self._on_folder_changed)
        self.progress_widget.error_occurred.connect(self.show_error)
        self.phrase_widget.filter_enabled_changed.connect(self._on_filter_enabled_changed)
    
    def _on_folder_changed(self, folder_path: str):
        """Handler cuando cambia carpeta seleccionada"""
        if folder_path:
            self.log_info(f"Carpeta destino: {folder_path}")
    
    def _on_filter_enabled_changed(self, enabled: bool):
        """Handler cuando se habilita/deshabilita el filtro de frases"""
        if enabled:
            self.log_info("Filtro de frases: HABILITADO")
        else:
            self.log_info("Filtro de frases: DESHABILITADO (procesará TODOS los correos)")
    
    def _on_start_clicked(self):
        """Valida parámetros e inicia extracción con ExtractorWorker"""
        params = self._recopilar_parametros()
        
        if not params['folder']:
            self.show_error("❌ Debe seleccionar una carpeta de destino")
            return
        
        has_date_filter = params['date_range'] is not None
        has_phrase_filter = len(params['phrases']) > 0
        filter_enabled = self.phrase_widget.is_filter_enabled()
        
        # ✅ VALIDACIÓN: Si filtro habilitado, debe haber frases
        if filter_enabled and not has_phrase_filter:
            self.show_error("❌ Debe especificar al menos una frase de búsqueda o deshabilitar el filtro")
            return
        
        # ⚠️ ADVERTENCIA: Comillas sin cerrar
        if filter_enabled and self.phrase_widget.has_unclosed_quotes():
            reply = QMessageBox.question(
                self,
                "Advertencia: Comilla sin cerrar",
                "Se detectó una comilla sin cerrar en el filtro de frases.\n\n"
                "Esto puede causar resultados inesperados.\n\n"
                "¿Desea continuar de todos modos?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.No:
                return
        
        outlook_folder = self.outlook_folder_widget.get_folder()
        if not outlook_folder:
            self.show_error("❌ Debe seleccionar una bandeja de Outlook")
            return
        
        self._set_running_state(True)
        self.progress_widget.reset()
        
        self.logger.separador()
        self.log_info("INICIANDO EXTRACCIÓN DE ADJUNTOS")
        self.logger.separador()
        self.log_info(f"Carpeta destino: {params['folder']}")
        self.log_info(f"Bandeja Outlook: {outlook_folder}")
        
        if has_date_filter:
            dt_from, dt_to = params['date_range']
            self.log_info(f"Filtro de fechas: {dt_from.strftime('%d/%m/%Y')} - {dt_to.strftime('%d/%m/%Y')}")
        
        # ✅ LOGGING MEJORADO: Mostrar información del filtro de frases
        if filter_enabled:
            if has_phrase_filter:
                num_frases = len(params['phrases'])
                self.log_info(f"Modo de búsqueda: {params['search_mode']}")
                self.log_info(f"Total de frases: {num_frases}")
                self.logger.separador(char="-", length=60)
                for i, frase in enumerate(params['phrases'], 1):
                    self.log_info(f"  {i}. {frase}")
                self.logger.separador(char="-", length=60)
        else:
            self.log_info("⚠️ FILTRO DE FRASES DESHABILITADO: Procesando TODOS los correos")
        
        try:
            fecha_inicio, fecha_fin = params['date_range'] if has_date_filter else (None, None)
            
            self.worker = ExtractorWorker(
                frases=params['phrases'],  # Será lista vacía si filtro deshabilitado
                destino=params['folder'],
                outlook_folder=outlook_folder,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin
            )
            
            self.worker.signals.finished.connect(self._on_worker_finished)
            self.worker.signals.error.connect(self._on_worker_error)
            self.worker.signals.message.connect(self._on_worker_message)
            self.worker.signals.progress.connect(self._on_worker_progress)
            self.worker.signals.state_changed.connect(self._on_worker_state)
            
            self.threadpool.start(self.worker)
            self.extraction_started.emit(params)
            
        except Exception as e:
            self._set_running_state(False)
            self.show_error(f"Error al iniciar extracción: {str(e)}")
    
    def _recopilar_parametros(self) -> dict:
        """Recopila parámetros de la UI"""
        return {
            'folder': self.folder_widget.get_folder(),
            'date_range': self.date_range_widget.get_range(),
            'phrases': self.phrase_widget.get_phrases(),  # Retorna [] si filtro deshabilitado
            'search_mode': self.phrase_widget.get_search_mode(),
            'filter_enabled': self.phrase_widget.is_filter_enabled()
        }
    
    def _on_cancel_clicked(self):
        """Cancela proceso en ejecución"""
        if self.worker:
            self.log_info("Cancelación solicitada por el usuario...")
            self.worker.cancel()
            self.extraction_cancelled.emit()
    
    def _set_running_state(self, running: bool):
        """Actualiza estado de controles durante ejecución"""
        self.start_btn.setEnabled(not running)
        self.cancel_btn.setEnabled(running)
        self.folder_widget.setEnabled(not running)
        self.date_range_widget.setEnabled(not running)
        self.phrase_widget.setEnabled(not running)
    
    @Slot(int, str)
    def update_progress(self, value: int, status: str):
        """Actualiza barra de progreso"""
        self.progress_widget.set_progress(value)
        self.progress_widget.set_status(status)
    
    @Slot(int, int, int)
    def update_stats(self, processed: int, success: int, errors: int):
        """Actualísticas"""
        self.progress_widget.set_stats(processed, success, errors)
    
    @Slot(dict)
    def on_extraction_complete(self, stats: dict):
        """Handler cuando termina extracción"""
        self._set_running_state(False)
        success = stats.get('adjuntos_fallidos', 0) == 0
        self.progress_widget.set_complete(success)
        self.logger.escribir_estadisticas(stats)
        self.log_success("✅ Extracción finalizada correctamente")
        self.extraction_finished.emit(stats)
    
    @Slot(str)
    def on_extraction_error(self, error_msg: str):
        """Handler cuando hay error"""
        self._set_running_state(False)
        self.show_error(f"Error en extracción: {error_msg}")
        self.progress_widget.set_complete(success=False, message=f"❌ Error: {error_msg}")
    
    @Slot(dict)
    def _on_worker_finished(self, resultado: dict):
        """Slot cuando el worker termina"""
        self.on_extraction_complete(resultado)
    
    @Slot(str)
    def _on_worker_error(self, error_msg: str):
        """Slot cuando error"""
        self.on_extraction_error(error_msg)
    
    @Slot(object, object, str)
    def _on_worker_message(self, fase, nivel, texto: str):
        """Slot para mensajes"""
        self.progress_widget.set_status(texto)
    
    @Slot(int, int, float)
    def _on_worker_progress(self, actual: int, total: int, porcentaje: float):
        """Slot para progreso"""
        self.progress_widget.set_progress(int(porcentaje))
        
        if hasattr(self.worker, 'extractor') and hasattr(self.worker.extractor, 'estadisticas'):
            stats = self.worker.extractor.estadisticas
            self.progress_widget.set_stats(
                processed=stats.correos_procesados,
                success=stats.adjuntos_descargados,
                errors=stats.adjuntos_fallidos
            )
    
    @Slot(object)
    def _on_worker_state(self, estado):
        """Slot para cambio de estado"""
        self.log_info(f"Estado: {estado.value}")