"""Worker de PySide6 para clasificación de documentos."""

from .base_worker import BaseWorker
from core.sign_classifier import ClasificadorDocumentos


class ClassifierWorker(BaseWorker):
    """
    Worker para ejecutar clasificación de documentos en thread separado.
    
    Conecta el backend core con la UI mediante signals de PySide6.
    """
    
    def __init__(self, carpeta_origen: str):
        """
        Inicializa el worker de clasificación.
        
        Args:
            carpeta_origen: Carpeta con documentos a clasificar
        """
        super().__init__()
        
        self.carpeta_origen = carpeta_origen
        
        # Crear backend con callbacks
        self.clasificador = ClasificadorDocumentos(
            callback_mensaje=self._on_mensaje,
            callback_progreso=self._on_progreso,
            callback_estado=self._on_estado
        )
    
    def process(self):
        """
        Ejecuta la clasificación de documentos.
        
        Returns:
            dict: Estadísticas del proceso
        """
        resultado = self.clasificador.clasificar(
            carpeta_origen=self.carpeta_origen
        )
        return resultado
    
    def _on_mensaje(self, fase, nivel, texto: str):
        """Callback para mensajes del backend"""
        if not self.is_cancelled():
            self.emit_message(fase, nivel, texto)
    
    def _on_progreso(self, actual: int, total: int, porcentaje: float):
        """Callback para progreso del backend"""
        if not self.is_cancelled():
            self.emit_progress(actual, total, porcentaje)
    
    def _on_estado(self, estado):
        """Callback para cambios de estado del backend"""
        if not self.is_cancelled():
            self.emit_state_changed(estado)
    
    def cancel(self):
        """Cancela la operación"""
        super().cancel()
        if hasattr(self.clasificador, 'cancelar'):
            self.clasificador.cancelar()