"""Worker de PySide6 para extracción de adjuntos de Outlook."""

from datetime import datetime
from typing import List

from .base_worker import BaseWorker
from core.email_extractor import ExtractorAdjuntosOutlook


class ExtractorWorker(BaseWorker):
    """
    Worker para ejecutar extracción de adjuntos en thread separado.
    
    Conecta el backend core con la UI mediante signals de PySide6.
    """
    
    def __init__(self, frases: List[str], destino: str, outlook_folder: str,
                 fecha_inicio: datetime, fecha_fin: datetime):
        """
        Inicializa el worker de extracción.
        
        Args:
            frases: Lista de frases para filtrar
            destino: Carpeta destino para adjuntos
            outlook_folder: Ruta de carpeta de Outlook
            fecha_inicio: Fecha inicial del rango
            fecha_fin: Fecha final del rango
        """
        super().__init__()
        
        self.frases = frases
        self.destino = destino
        self.outlook_folder = outlook_folder
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        
        # Crear backend con callbacks
        self.extractor = ExtractorAdjuntosOutlook(
            callback_mensaje=self._on_mensaje,
            callback_progreso=self._on_progreso,
            callback_estado=self._on_estado
        )
    
    def process(self):
        """
        Ejecuta la extracción de adjuntos.
        
        Returns:
            dict: Estadísticas del proceso
        """
        resultado = self.extractor.extraer_adjuntos(
            frases=self.frases,
            destino=self.destino,
            outlook_folder=self.outlook_folder,
            fecha_inicio=self.fecha_inicio,
            fecha_fin=self.fecha_fin
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
        if hasattr(self.extractor, 'cancelar'):
            self.extractor.cancelar()