"""Clasificador de documentos según estado de firma."""

import shutil
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path

from core.backend_base import (
    BackendBase,
    FaseProceso as FaseBase,
    NivelMensaje,
    EstadoProceso,
    EstadisticasBase
)


class FaseProceso(Enum):
    """Fases específicas del proceso de clasificación"""
    INICIAL = "inicial"
    CLASIFICANDO = "clasificando"
    FINALIZACION = "finalizacion"


@dataclass
class EstadisticasClasificacion(EstadisticasBase):
    """Estadísticas del proceso de clasificación"""
    total: int = 0
    firmados: int = 0
    sin_firmar: int = 0
    omitidos: int = 0
    errores: int = 0


class ClasificadorDocumentos(BackendBase):
    """
    Clasificador de documentos según estado de firma.
    
    Clasifica documentos en carpetas "Firmados" y "Sin Firmar" basándose
    en palabras clave en el nombre del archivo.
    """
    
    def __init__(self, 
                 callback_mensaje=None,
                 callback_progreso=None,
                 callback_estado=None):
        """Inicializa el clasificador"""
        super().__init__(callback_mensaje, callback_progreso, callback_estado)
        self.estadisticas = EstadisticasClasificacion()
        self.cancelado = False
    
    def validar_parametros(self, carpeta_origen: str) -> tuple[bool, str]:
        """Valida los parámetros de clasificación"""
        es_valido, mensaje = self._validar_carpeta_existe(carpeta_origen, "carpeta de origen")
        if not es_valido:
            return False, mensaje
        
        carpeta_path = Path(carpeta_origen)
        if not self._verificar_permisos_escritura(carpeta_path):
            return False, "No tiene permisos de escritura en la carpeta"
        
        return True, ""
    
    def _procesar_principal(self, carpeta_origen: str) -> dict:
        """Procesamiento principal de clasificación"""
        self.estadisticas = EstadisticasClasificacion()
        self.estadisticas.tiempo_inicio = datetime.now()
        self.cancelado = False
        
        try:
            self._cambiar_fase(FaseProceso.INICIAL)
            carpeta_path = Path(carpeta_origen)
            
            # Crear carpetas de destino
            carpeta_firmados = carpeta_path / "Documentos Firmados"
            carpeta_sin_firmar = carpeta_path / "Documentos sin Firmar"
            
            if not self._crear_carpeta_segura(carpeta_firmados):
                raise Exception("No se pudo crear carpeta de firmados")
            
            if not self._crear_carpeta_segura(carpeta_sin_firmar):
                raise Exception("No se pudo crear carpeta de sin firmar")
            
            self._enviar_mensaje(
                FaseProceso.INICIAL,
                NivelMensaje.SUCCESS,
                "Carpetas de destino creadas"
            )
            
            # Obtener archivos a procesar
            archivos = [f for f in carpeta_path.iterdir() if f.is_file()]
            total = len(archivos)
            self.estadisticas.total = total
            
            if total == 0:
                self._enviar_mensaje(
                    FaseProceso.INICIAL,
                    NivelMensaje.WARNING,
                    "No se encontraron archivos para clasificar"
                )
                self.estadisticas.tiempo_fin = datetime.now()
                return self._generar_reporte()
            
            self._enviar_mensaje(
                FaseProceso.INICIAL,
                NivelMensaje.INFO,
                f"Archivos encontrados: {total}"
            )
            
            # Iniciar clasificación
            self._cambiar_fase(FaseProceso.CLASIFICANDO)
            self._cambiar_estado(EstadoProceso.CLASIFICANDO)
            
            procesados = 0
            
            for archivo in archivos:
                if self.cancelado:
                    break
                
                self._verificar_cancelacion()
                self._verificar_pausa()
                
                self._clasificar_archivo(archivo, carpeta_firmados, carpeta_sin_firmar)
                
                procesados += 1
                self._actualizar_progreso(procesados, total)
                
                if procesados % 10 == 0 or procesados == total:
                    self._enviar_mensaje(
                        FaseProceso.CLASIFICANDO,
                        NivelMensaje.INFO,
                        f"Procesados: {procesados}/{total} ({(procesados/total)*100:.1f}%)"
                    )
            
            # Finalizar
            self._cambiar_fase(FaseProceso.FINALIZACION)
            self.estadisticas.tiempo_fin = datetime.now()
            
            if self.cancelado:
                self._cambiar_estado(EstadoProceso.CANCELADO)
            else:
                self._cambiar_estado(EstadoProceso.COMPLETADO)
                self._enviar_mensaje(
                    FaseProceso.FINALIZACION,
                    NivelMensaje.SUCCESS,
                    f"Clasificación completada: {self.estadisticas.firmados} firmados, "
                    f"{self.estadisticas.sin_firmar} sin firmar"
                )
            
            return self._generar_reporte()
            
        except InterruptedError:
            self.estadisticas.tiempo_fin = datetime.now()
            raise
    
    def _generar_reporte(self) -> dict:
        """Genera reporte final de estadísticas"""
        return {
            'total': self.estadisticas.total,
            'firmados': self.estadisticas.firmados,
            'sin_firmar': self.estadisticas.sin_firmar,
            'omitidos': self.estadisticas.omitidos,
            'errores': self.estadisticas.errores,
            'tiempo_total': self.estadisticas.tiempo_total
        }
    
    def cancelar(self):
        """Cancela el proceso"""
        super().cancelar()
        self.cancelado = True
    
    def _clasificar_archivo(self, archivo: Path, 
                           carpeta_firmados: Path, 
                           carpeta_sin_firmar: Path) -> str:
        """
        Clasifica un archivo individual según su nombre.
        
        Args:
            archivo: Archivo a clasificar
            carpeta_firmados: Carpeta destino para firmados
            carpeta_sin_firmar: Carpeta destino para sin firmar
            
        Returns:
            str: Resultado ('firmado', 'sin_firmar', 'omitido', 'error')
        """
        nombre_lower = archivo.name.lower()
        
        try:
            # Detectar "sin firmar" (prioridad)
            es_sin_firmar = (
                "sin firmar" in nombre_lower or 
                "sin_firmar" in nombre_lower or
                "sinfirmar" in nombre_lower or
                "not signed" in nombre_lower or
                "not_signed" in nombre_lower or
                "notsigned" in nombre_lower
            )
            
            if es_sin_firmar:
                destino = carpeta_sin_firmar / archivo.name
                shutil.move(str(archivo), str(destino))
                self.estadisticas.sin_firmar += 1
                self._enviar_mensaje(
                    FaseProceso.CLASIFICANDO,
                    NivelMensaje.WARNING,
                    f"⚠️ Sin firmar: {archivo.name}"
                )
                return 'sin_firmar'
            
            # Detectar "firmado"
            elif "firmado" in nombre_lower or "signed" in nombre_lower:
                destino = carpeta_firmados / archivo.name
                shutil.move(str(archivo), str(destino))
                self.estadisticas.firmados += 1
                self._enviar_mensaje(
                    FaseProceso.CLASIFICANDO,
                    NivelMensaje.SUCCESS,
                    f"✅ Firmado: {archivo.name}"
                )
                return 'firmado'
            
            # No coincide con ningún criterio
            else:
                self.estadisticas.omitidos += 1
                return 'omitido'
                
        except PermissionError:
            self.estadisticas.errores += 1
            self._enviar_mensaje(
                FaseProceso.CLASIFICANDO,
                NivelMensaje.ERROR,
                f"❌ Archivo bloqueado: {archivo.name}"
            )
            return 'error'
            
        except Exception as e:
            self.estadisticas.errores += 1
            self._enviar_mensaje(
                FaseProceso.CLASIFICANDO,
                NivelMensaje.ERROR,
                f"❌ Error con {archivo.name}: {str(e)}"
            )
            return 'error'
    
    def clasificar(self, carpeta_origen: str) -> dict:
        """
        Método principal para clasificar documentos.
        
        Args:
            carpeta_origen: Carpeta con archivos a clasificar
            
        Returns:
            dict: Estadísticas del proceso
        """
        return self.ejecutar(carpeta_origen)


# Exportar
__all__ = [
    'ClasificadorDocumentos',
    'FaseProceso',
    'NivelMensaje',
    'EstadoProceso',
    'EstadisticasClasificacion'
]