# ui/widgets/progress_widget.py
"""
Widget de progreso con barra, porcentaje y estado.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QProgressBar, QLabel
from PySide6.QtCore import Qt
from .base_widget import BaseWidget


class ProgressWidget(BaseWidget):
    """
    Widget para mostrar progreso de operaciones largas.
    
    Características:
    - Barra de progreso con porcentaje
    - Label de estado/mensaje
    - Estadísticas opcionales (procesados, errores, etc.)
    """
    
    def __init__(self, show_stats: bool = True, parent=None):
        """
        Args:
            show_stats: Si se muestran estadísticas detalladas
            parent: Widget padre
        """
        self.show_stats = show_stats
        super().__init__(parent)
    
    def _setup_ui(self):
        """Construye la interfaz del widget de progreso"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # === LÍNEA DE ESTADÍSTICAS SUPERIOR (con tiempo) ===
        if self.show_stats:
            stats_layout = QHBoxLayout()
            
            # Tiempo transcurrido
            self.stats_time = QLabel("⏱️ Tiempo: 00:00:00")
            self.stats_time.setProperty("class", "subtitle")
            
            # Adjuntos procesados
            self.stats_processed = QLabel("📄 Adjuntos: 0/0")
            self.stats_processed.setProperty("class", "subtitle")
            
            # Errores
            self.stats_errors = QLabel("⚠️ Errores: 0")
            self.stats_errors.setProperty("class", "subtitle")
            self.stats_errors.setStyleSheet(f"color: {self.get_theme_color('error')};")
            
            stats_layout.addWidget(self.stats_time)
            stats_layout.addWidget(self.stats_processed)
            stats_layout.addWidget(self.stats_errors)
            stats_layout.addStretch()
            
            layout.addLayout(stats_layout)
        
        # === BARRA DE PROGRESO ===
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")  # Mostrar porcentaje
        self.progress_bar.setMinimumHeight(30)
        
        # === LABEL DE ESTADO ===
        self.status_label = QLabel("Listo para iniciar...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.status_label.setWordWrap(True)
        
        # === ENSAMBLAR LAYOUT ===
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)
    
    def set_progress(self, value: int):
        """
        Establece el valor de la barra de progreso.
        
        Args:
            value: Porcentaje (0-100)
        """
        self.progress_bar.setValue(value)
    
    def set_time_elapsed(self, seconds: float):
        """
        Actualiza el tiempo transcurrido.
        
        Args:
            seconds: Segundos transcurridos
        """
        if not self.show_stats:
            return
        
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        time_str = f"⏱️ Tiempo: {hours:02d}:{minutes:02d}:{secs:02d}"
        self.stats_time.setText(time_str)
    
    def set_status(self, message: str):
        """
        Establece el mensaje de estado.
        
        Args:
            message: Mensaje a mostrar
        """
        self.status_label.setText(message)
    
    def update_progress(self, value: int, status: str = ""):
        """
        Actualiza progreso y estado simultáneamente.
        
        Args:
            value: Porcentaje (0-100)
            status: Mensaje de estado (opcional)
        """
        self.set_progress(value)
        if status:
            self.set_status(status)
    
    def set_stats(self, processed: int = None, total: int = None, errors: int = None):
        """
        Actualiza las estadísticas mostradas.
        
        Args:
            processed: Adjuntos procesados actualmente
            total: Total de adjuntos a procesar
            errors: Adjuntos con error
        """
        if not self.show_stats:
            return
        
        if processed is not None and total is not None:
            self.stats_processed.setText(f"📄 Adjuntos: {processed}/{total}")
        
        if errors is not None:
            self.stats_errors.setText(f"⚠️ Errores: {errors}")
    
    def reset(self):
        """Resetea el widget a estado inicial"""
        self.progress_bar.setValue(0)
        self.status_label.setText("Listo para iniciar...")
        
        if self.show_stats:
            self.stats_time.setText("⏱️ Tiempo: 00:00:00")
            self.stats_processed.setText("📄 Adjuntos: 0/0")
            self.stats_errors.setText("⚠️ Errores: 0")
    
    def set_indeterminate(self, indeterminate: bool = True):
        """
        Cambia la barra a modo indeterminado (sin porcentaje conocido).
        
        Args:
            indeterminate: True para modo indeterminado
        """
        if indeterminate:
            self.progress_bar.setMaximum(0)  # Modo indeterminado
            self.progress_bar.setMinimum(0)
        else:
            self.progress_bar.setMaximum(100)  # Modo normal
            self.progress_bar.setMinimum(0)
    
    def set_complete(self, success: bool = True, message: str = ""):
        """
        Marca el proceso como completado.
        
        Args:
            success: True si fue exitoso, False si hubo error
            message: Mensaje final (opcional)
        """
        if success:
            self.progress_bar.setValue(100)
            if not message:
                message = "✅ Proceso completado exitosamente"
            self.status_label.setText(message)
            self.status_label.setStyleSheet(f"color: {self.get_theme_color('success')};")
        else:
            if not message:
                message = "❌ Proceso finalizado con errores"
            self.status_label.setText(message)
            self.status_label.setStyleSheet(f"color: {self.get_theme_color('error')};")