"""Sistema de logging centralizado para MatrixMAE con gestión automática."""

import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


class MatrixLogger:
    """
    Gestor de logging centralizado híbrido para MatrixMAE.
    
    Características:
    - Logger único de sesión para toda la aplicación
    - Archivo separado para errores globales
    - Limpieza automática de logs antiguos (>30 días)
    - Rotación por número de archivos (mantiene últimas 50 sesiones)
    - Secciones diferenciadas por backend
    - Console output configurable
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls, carpeta_logs: Optional[str] = None):
        """Singleton: una sola instancia para toda la aplicación"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, carpeta_logs: Optional[str] = None):
        """
        Inicializa el logger (solo la primera vez).
        
        Args:
            carpeta_logs: Ruta de carpeta para logs. Si es None, usa './logs'
        """
        if self._initialized:
            return
            
        self._initialized = True
        
        # Determinar carpeta de logs
        if carpeta_logs is None:
            carpeta_logs = Path.cwd() / 'logs'
        else:
            carpeta_logs = Path(carpeta_logs)
        
        # Crear carpeta si no existe
        carpeta_logs.mkdir(parents=True, exist_ok=True)
        self.carpeta_logs = carpeta_logs
        
        # Limpiar logs antiguos ANTES de crear nuevos
        self._limpiar_logs_antiguos()
        self._rotar_logs_por_cantidad()
        
        # Timestamp para archivos de esta sesión
        self.timestamp = datetime.now().strftime("%d.%m.%Y_%H.%M.%S")
        
        # Crear logger principal
        self.logger = logging.getLogger("MatrixMAE")
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers.clear()  # Limpiar handlers existentes
        
        # Configurar archivo de sesión general (todas las operaciones)
        self.archivo_sesion = carpeta_logs / f"MatrixMAE_sesion_{self.timestamp}.log"
        handler_sesion = logging.FileHandler(
            self.archivo_sesion,
            mode='w',
            encoding='utf-8'
        )
        handler_sesion.setLevel(logging.INFO)
        handler_sesion.setFormatter(self._get_formatter())
        self.logger.addHandler(handler_sesion)
        
        # Configurar archivo de errores global
        self.archivo_errores = carpeta_logs / f"MatrixMAE_errores_{self.timestamp}.log"
        handler_errores = logging.FileHandler(
            self.archivo_errores,
            mode='w',
            encoding='utf-8'
        )
        handler_errores.setLevel(logging.ERROR)
        handler_errores.setFormatter(self._get_formatter(detailed=True))
        self.logger.addHandler(handler_errores)
        
        # Handler para consola (opcional, configurable)
        self.console_handler = None
        
        # Contexto actual (para secciones)
        self._contexto_actual = None
        
        # Escribir encabezado
        self._escribir_encabezado()
    
    def _get_formatter(self, detailed: bool = False) -> logging.Formatter:
        """
        Crea un formatter para los logs.
        
        Args:
            detailed: Si True, incluye información detallada (para errores)
        """
        if detailed:
            formato = '[%(asctime)s] [%(levelname)s] [%(funcName)s:%(lineno)d] %(message)s'
        else:
            formato = '[%(asctime)s] [%(levelname)s] %(message)s'
        
        return logging.Formatter(
            formato,
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    def _escribir_encabezado(self):
        """Escribe encabezado en los archivos de log"""
        separador = "=" * 80
        encabezado = f"""
{separador}
MATRIXMAE - LOG DE SESIÓN
{separador}
Inicio de sesión: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Carpeta de logs: {self.carpeta_logs.absolute()}
{separador}
"""
        self.logger.info(encabezado)
    
    def _limpiar_logs_antiguos(self, dias: int = 30):
        """
        Elimina logs con antigüedad mayor a X días.
        
        Args:
            dias: Número de días de antigüedad máxima (default: 30)
        """
        fecha_limite = datetime.now() - timedelta(days=dias)
        
        logs_eliminados = 0
        for archivo in self.carpeta_logs.glob("MatrixMAE_*.log"):
            try:
                fecha_modificacion = datetime.fromtimestamp(archivo.stat().st_mtime)
                if fecha_modificacion < fecha_limite:
                    archivo.unlink()
                    logs_eliminados += 1
            except Exception:
                pass  # Ignorar errores al eliminar archivos individuales
        
        if logs_eliminados > 0:
            print(f"✓ Limpieza automática: {logs_eliminados} logs antiguos eliminados")
    
    def _rotar_logs_por_cantidad(self, max_sesiones: int = 50):
        """
        Mantiene solo las últimas N sesiones de logs.
        
        Args:
            max_sesiones: Número máximo de pares de archivos a mantener (default: 50)
        """
        # Obtener todos los archivos de sesión (ordenados por fecha de modificación)
        archivos_sesion = sorted(
            self.carpeta_logs.glob("MatrixMAE_sesion_*.log"),
            key=lambda f: f.stat().st_mtime,
            reverse=True
        )
        
        archivos_errores = sorted(
            self.carpeta_logs.glob("MatrixMAE_errores_*.log"),
            key=lambda f: f.stat().st_mtime,
            reverse=True
        )
        
        # Eliminar los más antiguos si exceden el límite
        logs_eliminados = 0
        
        for archivo in archivos_sesion[max_sesiones:]:
            try:
                archivo.unlink()
                logs_eliminados += 1
            except Exception:
                pass
        
        for archivo in archivos_errores[max_sesiones:]:
            try:
                archivo.unlink()
                logs_eliminados += 1
            except Exception:
                pass
        
        if logs_eliminados > 0:
            print(f"✓ Rotación automática: {logs_eliminados} logs antiguos eliminados")
    
    def iniciar_seccion(self, nombre: str):
        """
        Inicia una nueva sección en el log (para diferenciar backends).
        
        Args:
            nombre: Nombre de la sección (ej: 'ExtractorAdjuntosOutlook')
        """
        self._contexto_actual = nombre
        separador = "=" * 80
        self.logger.info(f"\n{separador}")
        self.logger.info(f"SECCIÓN: {nombre.upper()}")
        self.logger.info(f"Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(separador)
    
    def finalizar_seccion(self):
        """Finaliza la sección actual"""
        if self._contexto_actual:
            separador = "=" * 80
            self.logger.info(separador)
            self.logger.info(f"FIN DE SECCIÓN: {self._contexto_actual.upper()}")
            self.logger.info(f"Finalización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            self.logger.info(f"{separador}\n")
            self._contexto_actual = None
    
    def habilitar_consola(self, nivel: int = logging.INFO):
        """
        Habilita output a consola.
        
        Args:
            nivel: Nivel mínimo para mostrar en consola (default: INFO)
        """
        if self.console_handler is None:
            self.console_handler = logging.StreamHandler(sys.stdout)
            self.console_handler.setLevel(nivel)
            self.console_handler.setFormatter(self._get_formatter())
            self.logger.addHandler(self.console_handler)
    
    def deshabilitar_consola(self):
        """Deshabilita output a consola"""
        if self.console_handler:
            self.logger.removeHandler(self.console_handler)
            self.console_handler = None
    
    # Métodos de logging
    def debug(self, mensaje: str):
        """Log nivel DEBUG"""
        self.logger.debug(mensaje)
    
    def info(self, mensaje: str):
        """Log nivel INFO"""
        self.logger.info(mensaje)
    
    def success(self, mensaje: str):
        """Log de éxito (INFO con prefijo)"""
        self.logger.info(f"✅ {mensaje}")
    
    def warning(self, mensaje: str):
        """Log nivel WARNING"""
        self.logger.warning(f"⚠️ {mensaje}")
    
    def error(self, mensaje: str, exc_info: bool = False):
        """
        Log nivel ERROR.
        
        Args:
            mensaje: Mensaje de error
            exc_info: Si True, incluye traceback de excepción actual
        """
        self.logger.error(f"❌ {mensaje}", exc_info=exc_info)
    
    def critical(self, mensaje: str, exc_info: bool = False):
        """Log nivel CRITICAL"""
        self.logger.critical(f"🔥 {mensaje}", exc_info=exc_info)
    
    def separador(self, char: str = "-", length: int = 80):
        """Escribe una línea separadora en el log"""
        self.logger.info(char * length)
    
    def escribir_estadisticas(self, stats: dict, titulo: str = "ESTADÍSTICAS"):
        """
        Escribe estadísticas en el log.
        
        Args:
            stats: Diccionario con estadísticas
            titulo: Título de la sección de estadísticas
        """
        self.separador()
        self.logger.info(titulo)
        self.separador()
        
        for clave, valor in stats.items():
            if isinstance(valor, float):
                self.logger.info(f"{clave}: {valor:.2f}")
            else:
                self.logger.info(f"{clave}: {valor}")
        
        self.separador()
    
    def finalizar(self, mensaje: str = "Sesión finalizada"):
        """
        Finaliza la sesión de logging.
        
        Args:
            mensaje: Mensaje de finalización
        """
        separador = "=" * 80
        self.logger.info(f"\n{separador}")
        self.logger.info(mensaje)
        self.logger.info(f"Hora de finalización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(separador)
        
        # Cerrar handlers
        for handler in self.logger.handlers[:]:
            handler.close()
            self.logger.removeHandler(handler)


def get_logger(carpeta_logs: Optional[str] = None) -> MatrixLogger:
    """
    Factory function para obtener el logger único.
    
    Args:
        carpeta_logs: Carpeta para los archivos de log (solo primera vez)
        
    Returns:
        MatrixLogger configurado (singleton)
    """
    return MatrixLogger(carpeta_logs)


# Ejemplo de uso
if __name__ == "__main__":
    # Crear logger (singleton)
    logger = get_logger("./logs")
    logger.habilitar_consola()
    
    # Sección 1: Extractor
    logger.iniciar_seccion("ExtractorAdjuntosOutlook")
    logger.info("Iniciando extracción de adjuntos")
    logger.success("100 adjuntos extraídos")
    logger.warning("2 archivos omitidos por tamaño")
    
    stats_extractor = {
        'total_emails': 1000,
        'adjuntos_extraidos': 100,
        'tiempo_total': 45.67
    }
    logger.escribir_estadisticas(stats_extractor, "ESTADÍSTICAS - EXTRACTOR")
    logger.finalizar_seccion()
    
    # Sección 2: Clasificador
    logger.iniciar_seccion("ClasificadorDocumentos")
    logger.info("Iniciando clasificación de documentos")
    logger.success("85 documentos clasificados")
    logger.error("Error al procesar documento corrupto")
    
    stats_clasificador = {
        'total_documentos': 100,
        'firmados': 60,
        'sin_firma': 25,
        'tiempo_total': 23.45
    }
    logger.escribir_estadisticas(stats_clasificador, "ESTADÍSTICAS - CLASIFICADOR")
    logger.finalizar_seccion()
    
    # Finalizar sesión
    logger.finalizar()
    
    print(f"\n✓ Logs guardados en:")
    print(f"  Sesión: {logger.archivo_sesion}")
    print(f"  Errores: {logger.archivo_errores}")