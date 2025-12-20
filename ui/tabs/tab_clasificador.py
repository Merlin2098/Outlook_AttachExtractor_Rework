# ui/tabs/tab_clasificador.py
"""
Tab completo para clasificación de documentos por firma.
"""

from PySide6.QtWidgets import (
    QGroupBox, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel
)
from PySide6.QtCore import Signal, Slot, QThreadPool
from .base_tab import BaseTab
from ui.widgets import (
    FolderSelectorWidget,
    ProgressWidget
)
from workers import ClassifierWorker


class TabClasificador(BaseTab):
    """
    Tab de clasificación de documentos por firma digital.
    
    Signals:
        classification_started: Emitido al iniciar clasificación (dict con parámetros)
        classification_finished: Emitido al terminar clasificación (dict con estadísticas)
        classification_cancelled: Emitido al cancelar clasificación
    """
    
    classification_started = Signal(dict)
    classification_finished = Signal(dict)
    classification_cancelled = Signal()
    
    def __init__(self, parent=None):
        super().__init__("Clasificador", parent)
        
        # Backend y worker
        self.backend = None
        self.worker = None
        self.threadpool = QThreadPool.globalInstance()
    
    def _setup_ui(self):
        """Construye interfaz del clasificador"""
        
        # === SECCIÓN: CARPETA ORIGEN ===
        source_group = QGroupBox("📂 Carpeta a Clasificar")
        source_layout = QVBoxLayout()
        
        self.source_widget = FolderSelectorWidget(
            placeholder="Selecciona carpeta con documentos PDF...",
            button_text="📂 Seleccionar Carpeta"
        )
        source_layout.addWidget(self.source_widget)
        source_group.setLayout(source_layout)
        
        # === SECCIÓN: INFORMACIÓN ===
        info_group = QGroupBox("ℹ️ Información")
        info_layout = QVBoxLayout()
        
        info_text = QLabel(
            "El clasificador analizará todos los archivos PDF en la carpeta seleccionada\n"
            "y los organizará en dos subcarpetas:\n\n"
            "• 📝 <b>Firmados</b>: Documentos con firma digital válida\n"
            "• ❌ <b>Sin Firmar</b>: Documentos sin firma o con firma inválida\n\n"
            "Los archivos originales NO se modifican, solo se copian a las subcarpetas."
        )
        info_text.setWordWrap(True)
        info_text.setProperty("class", "subtitle")
        
        info_layout.addWidget(info_text)
        info_group.setLayout(info_layout)
        
        # === SECCIÓN: PROGRESO ===
        progress_group = QGroupBox("📊 Progreso de Clasificación")
        progress_layout = QVBoxLayout()
        
        self.progress_widget = ProgressWidget(show_stats=True)
        progress_layout.addWidget(self.progress_widget)
        progress_group.setLayout(progress_layout)
        
        # === BOTONES DE ACCIÓN ===
        actions_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("▶️ Iniciar Clasificación")
        self.start_btn.setMinimumHeight(40)
        self.start_btn.clicked.connect(self._on_start_clicked)
        
        self.cancel_btn = QPushButton("⏹️ Cancelar Proceso")
        self.cancel_btn.setMinimumHeight(40)
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self._on_cancel_clicked)
        
        actions_layout.addWidget(self.start_btn)
        actions_layout.addWidget(self.cancel_btn)
        
        # === ENSAMBLAR LAYOUT PRINCIPAL ===
        self.main_layout.addWidget(source_group)
        self.main_layout.addWidget(info_group)
        self.main_layout.addWidget(progress_group)
        self.main_layout.addLayout(actions_layout)
        self.main_layout.addStretch()
    
    def _connect_signals(self):
        """Conecta señales internas"""
        # Cuando cambia carpeta, registrar en log
        self.source_widget.folder_changed.connect(self._on_folder_changed)
        
        # Conectar errores del progress widget
        self.progress_widget.error_occurred.connect(self.show_error)
    
    def _on_folder_changed(self, folder_path: str):
        """
        Handler cuando cambia carpeta seleccionada.
        
        Args:
            folder_path: Nueva ruta de carpeta
        """
        if folder_path:
            self.log_info(f"Carpeta origen: {folder_path}")
    
    def _on_start_clicked(self):
        """Valida parámetros e inicia clasificación con ClassifierWorker"""
        folder = self.source_widget.get_folder()
        
        # === VALIDACIÓN ===
        if not folder:
            self.show_error("❌ Debe seleccionar una carpeta a clasificar")
            return
        
        params = {'folder': folder}
        
        # === CAMBIAR ESTADO DE UI ===
        self._set_running_state(True)
        self.progress_widget.reset()
        
        # === LOG DE INICIO ===
        self.logger.separador()
        self.log_info("INICIANDO CLASIFICACIÓN DE DOCUMENTOS")
        self.logger.separador()
        self.log_info(f"Carpeta origen: {folder}")
        
        # === CREAR WORKER ===
        try:
            self.worker = ClassifierWorker(carpeta_origen=folder)
            
            # Conectar señales del worker
            self.worker.signals.finished.connect(self._on_worker_finished)
            self.worker.signals.error.connect(self._on_worker_error)
            self.worker.signals.message.connect(self._on_worker_message)
            self.worker.signals.progress.connect(self._on_worker_progress)
            self.worker.signals.state_changed.connect(self._on_worker_state)
            
            # Ejecutar en threadpool
            self.threadpool.start(self.worker)
            
            # Emitir señal de inicio
            self.classification_started.emit(params)
            
        except Exception as e:
            self._set_running_state(False)
            self.show_error(f"Error al iniciar clasificación: {str(e)}")
    
    def _on_cancel_clicked(self):
        """Cancela proceso en ejecución usando worker"""
        if self.worker:
            self.log_info("Cancelación solicitada por el usuario...")
            self.worker.cancel()
            self.classification_cancelled.emit()
    
    def _set_running_state(self, running: bool):
        """
        Actualiza estado de controles durante ejecución.
        
        Args:
            running: True si hay proceso en curso
        """
        self.start_btn.setEnabled(not running)
        self.cancel_btn.setEnabled(running)
        self.source_widget.setEnabled(not running)
    
    @Slot(int, str)
    def update_progress(self, value: int, status: str):
        """
        Actualiza barra de progreso desde thread externo.
        
        Args:
            value: Porcentaje (0-100)
            status: Mensaje de estado
        """
        self.progress_widget.set_progress(value)
        self.progress_widget.set_status(status)
    
    @Slot(int, int, int)
    def update_stats(self, processed: int, success: int, errors: int):
        """
        Actualiza estadísticas desde thread externo.
        
        Args:
            processed: Total procesados
            success: Firmados
            errors: Sin firma/errores
        """
        self.progress_widget.set_stats(processed, success, errors)
    
    @Slot(dict)
    def on_classification_complete(self, stats: dict):
        """
        Handler cuando termina clasificación.
        
        Args:
            stats: Diccionario con estadísticas finales
        """
        self._set_running_state(False)
        
        # Mostrar resultado
        success = stats.get('errores', 0) == 0
        self.progress_widget.set_complete(success)
        
        # Log de estadísticas
        self.logger.escribir_estadisticas(stats)
        self.log_success("✅ Clasificación finalizada correctamente")
        
        # Emitir señal
        self.classification_finished.emit(stats)
    
    @Slot(str)
    def on_classification_error(self, error_msg: str):
        """
        Handler cuando hay error en clasificación.
        
        Args:
            error_msg: Mensaje de error
        """
        self._set_running_state(False)
        self.show_error(f"Error en clasificación: {error_msg}")
        self.progress_widget.set_complete(success=False, message=f"❌ Error: {error_msg}")
    
    # === SLOTS PARA SEÑALES DEL WORKER ===
    
    @Slot(dict)
    def _on_worker_finished(self, resultado: dict):
        """Slot cuando el worker termina exitosamente"""
        self.on_classification_complete(resultado)
    
    @Slot(str)
    def _on_worker_error(self, error_msg: str):
        """Slot cuando el worker termina con error"""
        self.on_classification_error(error_msg)
    
    @Slot(object, object, str)
    def _on_worker_message(self, fase, nivel, texto: str):
        """Slot para mensajes del worker"""
        self.progress_widget.set_status(texto)
    
    @Slot(int, int, float)
    def _on_worker_progress(self, actual: int, total: int, porcentaje: float):
        """Slot para progreso del worker"""
        self.progress_widget.set_progress(int(porcentaje))
        
        # Actualizar estadísticas
        if hasattr(self.worker, 'clasificador') and hasattr(self.worker.clasificador, 'estadisticas'):
            stats = self.worker.clasificador.estadisticas
            self.progress_widget.set_stats(
                processed=stats.total,
                success=stats.firmados,
                errors=stats.errores
            )
    
    @Slot(object)
    def _on_worker_state(self, estado):
        """Slot para cambio de estado del worker"""
        self.log_info(f"Estado: {estado.value}")