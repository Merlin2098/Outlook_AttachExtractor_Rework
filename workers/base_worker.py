# ui/workers/base_worker.py
"""
Worker base para ejecutar operaciones en threads separados.
Proporciona señales y manejo de COM para todos los workers.
"""

import pythoncom
from PySide6.QtCore import QRunnable, Signal, QObject


class WorkerSignals(QObject):
    """
    Señales para comunicación worker → UI.
    
    Signals:
        finished: Emitido cuando termina exitosamente (dict con estadísticas)
        error: Emitido cuando hay error (str con mensaje)
        message: Emitido para mensajes del backend (fase, nivel, texto)
        progress: Emitido para progreso (actual, total, porcentaje)
        state_changed: Emitido cuando cambia el estado del backend (EstadoProceso)
    """
    finished = Signal(dict)
    error = Signal(str)
    message = Signal(object, object, str)  # fase, nivel, texto
    progress = Signal(int, int, float)      # actual, total, porcentaje
    state_changed = Signal(object)          # estado


class BaseWorker(QRunnable):
    """
    Worker base abstracto para operaciones en thread separado.
    
    Características:
    - Inicializa/limpia COM automáticamente
    - Maneja cancelación
    - Emite señales para comunicación con UI
    - Auto-delete tras finalizar
    """
    
    def __init__(self):
        super().__init__()
        
        # Señales para comunicación
        self.signals = WorkerSignals()
        
        # Control de cancelación
        self._cancelled = False
        
        # Auto-delete cuando termine
        self.setAutoDelete(True)
    
    def run(self):
        """
        Ejecuta el worker en thread separado.
        
        Flujo:
        1. Inicializa COM (requerido para Outlook)
        2. Ejecuta método process() (implementado por subclases)
        3. Emite señal finished con resultado
        4. Si hay error, emite señal error
        5. Limpia COM
        """
        resultado = {}
        
        try:
            # Inicializar COM (necesario para win32com)
            pythoncom.CoInitialize()
            
            # Ejecutar proceso principal (implementado por subclases)
            resultado = self.process()
            
            # Emitir señal de éxito
            if not self._cancelled:
                self.signals.finished.emit(resultado)
            
        except Exception as e:
            # Emitir señal de error
            if not self._cancelled:
                error_msg = str(e)
                self.signals.error.emit(error_msg)
            
        finally:
            # Limpiar COM
            try:
                pythoncom.CoUninitialize()
            except:
                pass
    
    def process(self):
        """
        Método abstracto para ejecutar la operación principal.
        DEBE ser implementado por subclases.
        
        Returns:
            dict: Resultado de la operación
        """
        raise NotImplementedError("Subclases deben implementar process()")
    
    def cancel(self):
        """Marca el worker como cancelado"""
        self._cancelled = True
    
    def is_cancelled(self) -> bool:
        """
        Verifica si el worker fue cancelado.
        
        Returns:
            bool: True si fue cancelado
        """
        return self._cancelled
    
    # === MÉTODOS HELPERS PARA EMITIR SEÑALES ===
    
    def emit_message(self, fase, nivel, texto: str):
        """
        Emite señal de mensaje.
        
        Args:
            fase: Fase del proceso
            nivel: Nivel del mensaje
            texto: Mensaje
        """
        if not self._cancelled:
            self.signals.message.emit(fase, nivel, texto)
    
    def emit_progress(self, actual: int, total: int, porcentaje: float):
        """
        Emite señal de progreso.
        
        Args:
            actual: Cantidad actual procesada
            total: Cantidad total
            porcentaje: Porcentaje (0-100)
        """
        if not self._cancelled:
            self.signals.progress.emit(actual, total, porcentaje)
    
    def emit_state_changed(self, estado):
        """
        Emite señal de cambio de estado.
        
        Args:
            estado: Nuevo estado del backend
        """
        if not self._cancelled:
            self.signals.state_changed.emit(estado)


# Exportar
__all__ = ['BaseWorker', 'WorkerSignals']