"""Clase base abstracta para backends de procesamiento con funcionalidad común."""

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from threading import Event
from typing import Optional, Callable

from utils.logger import get_logger
from utils.date_handler import validate_date_range


class FaseProceso(Enum):
    """Fases del proceso (pueden ser extendidas por subclases)"""
    INICIAL = "inicial"
    PROCESANDO = "procesando"
    FINALIZACION = "finalizacion"


class NivelMensaje(Enum):
    """Niveles de mensajes de log"""
    DEBUG = "debug"
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class EstadoProceso(Enum):
    """Estados posibles del proceso"""
    DETENIDO = "detenido"
    INICIANDO = "iniciando"
    FILTRANDO = "filtrando"
    PROCESANDO = "procesando"
    CLASIFICANDO = "clasificando"
    EN_EJECUCION = "en_ejecucion"
    PAUSADO = "pausado"
    COMPLETADO = "completado"
    CANCELADO = "cancelado"
    ERROR = "error"


@dataclass
class EstadisticasBase:
    """Estadísticas base del proceso"""
    tiempo_inicio: Optional[datetime] = None
    tiempo_fin: Optional[datetime] = None
    
    @property
    def tiempo_total(self) -> float:
        """Tiempo total en segundos"""
        if self.tiempo_inicio and self.tiempo_fin:
            return (self.tiempo_fin - self.tiempo_inicio).total_seconds()
        return 0.0


class BackendBase(ABC):
    """
    Clase base abstracta para backends de procesamiento.
    
    Proporciona: callbacks unificados, control de estados, logging centralizado,
    validación base y utilidades comunes.
    """
    
    def __init__(self,
                 callback_mensaje: Optional[Callable] = None,
                 callback_progreso: Optional[Callable] = None,
                 callback_estado: Optional[Callable] = None):
        """
        Inicializa el backend.
        
        Args:
            callback_mensaje: Función para mensajes (fase, nivel, texto)
            callback_progreso: Función para progreso (actual, total, porcentaje)
            callback_estado: Función para cambios de estado (EstadoProceso)
        """
        self.callback_mensaje = callback_mensaje or self._callback_default
        self.callback_progreso = callback_progreso or self._callback_default
        self.callback_estado = callback_estado or self._callback_default
        
        self.estado_actual = EstadoProceso.DETENIDO
        self.fase_actual = FaseProceso.INICIAL
        
        # Control de pausa/cancelación
        self._event_pausa = Event()
        self._event_cancelar = Event()
        self._event_pausa.set()
        
        # Logger centralizado único (singleton compartido)
        self.logger = get_logger()
        
        # Nombre de la sección para este backend
        self._nombre_seccion = self.__class__.__name__
    
    def _callback_default(self, *args, **kwargs):
        """Callback por defecto que no hace nada"""
        pass
    
    @abstractmethod
    def validar_parametros(self, *args, **kwargs) -> tuple[bool, str]:
        """
        Valida los parámetros específicos del backend.
        
        Returns:
            (bool, str): (es_valido, mensaje_error)
        """
        pass
    
    @abstractmethod
    def _procesar_principal(self, *args, **kwargs) -> dict:
        """
        Método principal de procesamiento (lógica específica).
        
        Returns:
            dict: Estadísticas del proceso
        """
        pass
    
    @abstractmethod
    def _generar_reporte(self) -> dict:
        """
        Genera reporte final de estadísticas.
        
        Returns:
            dict: Reporte con estadísticas
        """
        pass
    
    def _enviar_mensaje(self, fase: FaseProceso, nivel: NivelMensaje, texto: str):
        """
        Envía un mensaje con contexto de fase y nivel.
        
        Args:
            fase: Fase actual del proceso
            nivel: Nivel del mensaje
            texto: Contenido del mensaje
        """
        self.callback_mensaje(fase, nivel, texto)
        
        # Escribir en log según nivel
        if nivel == NivelMensaje.DEBUG:
            self.logger.debug(texto)
        elif nivel == NivelMensaje.INFO:
            self.logger.info(texto)
        elif nivel == NivelMensaje.SUCCESS:
            self.logger.success(texto)
        elif nivel == NivelMensaje.WARNING:
            self.logger.warning(texto)
        elif nivel == NivelMensaje.ERROR:
            self.logger.error(texto)
    
    def _actualizar_progreso(self, actual: int, total: int):
        """
        Actualiza el progreso del proceso.
        
        Args:
            actual: Cantidad actual procesada
            total: Cantidad total a procesar
        """
        porcentaje = (actual / total * 100) if total > 0 else 0.0
        self.callback_progreso(actual, total, porcentaje)
    
    def _cambiar_estado(self, nuevo_estado: EstadoProceso):
        """
        Cambia el estado del proceso y notifica.
        
        Args:
            nuevo_estado: Nuevo estado del proceso
        """
        self.estado_actual = nuevo_estado
        self.callback_estado(nuevo_estado)
        self.logger.info(f"Estado: {nuevo_estado.value}")
    
    def _cambiar_fase(self, nueva_fase: FaseProceso):
        """
        Cambia la fase del proceso.
        
        Args:
            nueva_fase: Nueva fase del proceso
        """
        self.fase_actual = nueva_fase
        self._enviar_mensaje(
            nueva_fase,
            NivelMensaje.INFO,
            f"Fase: {nueva_fase.value}"
        )
    
    def pausar(self):
        """Pausa el proceso"""
        estados_pausables = (
            EstadoProceso.EN_EJECUCION,
            EstadoProceso.FILTRANDO,
            EstadoProceso.PROCESANDO,
            EstadoProceso.CLASIFICANDO
        )
        if self.estado_actual in estados_pausables:
            self._estado_antes_pausa = self.estado_actual
            self._event_pausa.clear()
            self._cambiar_estado(EstadoProceso.PAUSADO)
            self._enviar_mensaje(
                self.fase_actual,
                NivelMensaje.WARNING,
                "Proceso pausado"
            )
    
    def reanudar(self):
        """Reanuda el proceso pausado"""
        if self.estado_actual == EstadoProceso.PAUSADO:
            self._event_pausa.set()
            if hasattr(self, '_estado_antes_pausa'):
                self._cambiar_estado(self._estado_antes_pausa)
            else:
                self._cambiar_estado(EstadoProceso.EN_EJECUCION)
            self._enviar_mensaje(
                self.fase_actual,
                NivelMensaje.SUCCESS,
                "Proceso reanudado"
            )
    
    def cancelar(self):
        """Cancela el proceso"""
        if self.estado_actual != EstadoProceso.DETENIDO:
            self._event_cancelar.set()
            if self.estado_actual == EstadoProceso.PAUSADO:
                self._event_pausa.set()
            self._enviar_mensaje(
                self.fase_actual,
                NivelMensaje.WARNING,
                "Cancelación solicitada"
            )
    
    def _verificar_pausa(self):
        """Verifica si el proceso está pausado y espera"""
        self._event_pausa.wait()
    
    def _verificar_cancelacion(self):
        """Verifica si se solicitó cancelación"""
        if self._event_cancelar.is_set():
            raise InterruptedError("Proceso cancelado por el usuario")
    
    def _resetear_control(self):
        """Resetea los eventos de control"""
        self._event_pausa.set()
        self._event_cancelar.clear()
    
    def _manejar_nombre_duplicado(self, ruta: Path) -> Path:
        """
        Maneja nombres de archivo duplicados agregando sufijo numérico.
        
        Args:
            ruta: Ruta del archivo
            
        Returns:
            Path: Ruta única (original o con sufijo)
        """
        if not ruta.exists():
            return ruta
        
        carpeta = ruta.parent
        nombre_base = ruta.stem
        extension = ruta.suffix
        contador = 1
        
        while True:
            ruta_archivo = carpeta / f"{nombre_base}_{contador}{extension}"
            if not ruta_archivo.exists():
                return ruta_archivo
            
            contador += 1
            
            if contador > 1000:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                ruta_archivo = carpeta / f"{nombre_base}_{timestamp}{extension}"
                break
        
        return ruta_archivo
    
    def _crear_carpeta_segura(self, ruta: Path) -> bool:
        """
        Crea una carpeta de forma segura.
        
        Args:
            ruta: Ruta de la carpeta a crear
            
        Returns:
            bool: True si se creó exitosamente
        """
        try:
            ruta.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            self._enviar_mensaje(
                self.fase_actual,
                NivelMensaje.ERROR,
                f"Error al crear carpeta {ruta}: {str(e)}"
            )
            return False
    
    def _verificar_permisos_escritura(self, ruta: Path) -> bool:
        """
        Verifica permisos de escritura en una ruta.
        
        Args:
            ruta: Ruta a verificar
            
        Returns:
            bool: True si tiene permisos de escritura
        """
        return os.access(str(ruta), os.W_OK)
    
    def _validar_carpeta_existe(self, carpeta: str, nombre: str = "carpeta") -> tuple[bool, str]:
        """
        Valida que una carpeta existe.
        
        Args:
            carpeta: Ruta de la carpeta
            nombre: Nombre descriptivo de la carpeta
            
        Returns:
            (bool, str): (es_valido, mensaje_error)
        """
        if not carpeta or not carpeta.strip():
            return False, f"Debe seleccionar una {nombre}"
        
        if not os.path.exists(carpeta):
            return False, f"La {nombre} no existe"
        
        if not os.path.isdir(carpeta):
            return False, f"La ruta no es una {nombre} válida"
        
        return True, ""
    
    def _validar_rango_fechas(self, fecha_inicio: datetime, fecha_fin: datetime) -> tuple[bool, str]:
        """
        Valida un rango de fechas usando date_handler para evitar errores de timezone.
        
        Args:
            fecha_inicio: Fecha inicial
            fecha_fin: Fecha final
            
        Returns:
            (bool, str): (es_valido, mensaje_error)
        """
        return validate_date_range(fecha_inicio, fecha_fin)
    
    def ejecutar(self, *args, **kwargs) -> dict:
        """
        Template method para ejecutar el proceso completo.
        
        Coordina: validación, inicialización, procesamiento y finalización.
        
        Returns:
            dict: Estadísticas del proceso
        """
        try:
            # Validación de parámetros
            es_valido, mensaje_error = self.validar_parametros(*args, **kwargs)
            if not es_valido:
                self._enviar_mensaje(
                    FaseProceso.INICIAL,
                    NivelMensaje.ERROR,
                    f"Validación fallida: {mensaje_error}"
                )
                raise ValueError(mensaje_error)
            
            # Iniciar sección en el log
            self.logger.iniciar_seccion(self._nombre_seccion)
            
            # Resetear control y cambiar estado
            self._resetear_control()
            self._cambiar_estado(EstadoProceso.INICIANDO)
            
            # Ejecutar procesamiento principal
            tiempo_inicio = datetime.now()
            resultado = self._procesar_principal(*args, **kwargs)
            tiempo_fin = datetime.now()
            
            resultado['tiempo_total'] = (tiempo_fin - tiempo_inicio).total_seconds()
            
            # Cambiar estado si no fue cancelado
            if not self._event_cancelar.is_set():
                self._cambiar_estado(EstadoProceso.COMPLETADO)
            
            # Escribir estadísticas en log
            self.logger.escribir_estadisticas(
                resultado, 
                f"ESTADÍSTICAS FINALES - {self._nombre_seccion.upper()}"
            )
            
            # Finalizar sección
            self.logger.finalizar_seccion()
            
            return resultado
            
        except InterruptedError:
            self._cambiar_estado(EstadoProceso.CANCELADO)
            self.logger.finalizar_seccion()
            return self._generar_reporte()
            
        except Exception as e:
            self._cambiar_estado(EstadoProceso.ERROR)
            self._enviar_mensaje(
                self.fase_actual,
                NivelMensaje.ERROR,
                f"Error: {str(e)}"
            )
            self.logger.error(f"Error durante ejecución: {str(e)}", exc_info=True)
            self.logger.finalizar_seccion()
            raise
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(estado={self.estado_actual.value}, fase={self.fase_actual.value})"