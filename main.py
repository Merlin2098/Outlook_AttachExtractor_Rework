#!/usr/bin/env python3
# main.py
"""
Punto de entrada de MatrixMAE.
Inicializa aplicación con splash screen y logging centralizado.
"""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

# Asegurar que el directorio raíz esté en sys.path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.config_manager import ConfigManager
from ui.theme_manager import ThemeManager
from ui.splash_screen import SplashScreen
from ui.main_window import MainWindow
from utils.logger import get_logger


def main():
    """
    Función principal de la aplicación.
    
    Flujo:
    1. Inicializar sistema de logging centralizado
    2. Crear QApplication
    3. Aplicar tema global
    4. Mostrar splash screen (si habilitado)
    5. Inicializar componentes
    6. Mostrar ventana principal
    7. Cerrar splash
    8. Ejecutar event loop
    9. Finalizar logging
    """
    
    # === INICIALIZAR LOGGING ===
    # Logger único para toda la sesión (singleton)
    logger = get_logger()
    logger.habilitar_consola()  # Habilitar output a consola durante desarrollo
    
    logger.info("Iniciando MatrixMAE...")
    
    # === CREAR APLICACIÓN ===
    app = QApplication(sys.argv)
    app.setApplicationName("MatrixMAE")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("MatrixMAE")
    
    logger.info("QApplication creada exitosamente")
    
    # === CONFIGURACIÓN ===
    config = ConfigManager()
    theme_manager = ThemeManager()
    
    # Aplicar tema global
    stylesheet = theme_manager.get_stylesheet()
    app.setStyleSheet(stylesheet)
    
    logger.info(f"Tema aplicado: {theme_manager.get_current_theme()}")
    
    # === SPLASH SCREEN ===
    show_splash = config.get('app.show_splash', True)
    
    if show_splash:
        logger.info("Mostrando splash screen...")
        
        # Obtener ruta del icono
        icon_path = config.get_icon_path()
        icon_str = str(icon_path) if icon_path else None
        
        # Crear y mostrar splash
        splash = SplashScreen(icon_path=icon_str)
        splash.show()
        
        # Procesar eventos para mostrar splash
        app.processEvents()
        
        # Simular carga de componentes
        splash.update_progress(20, "Cargando configuración...")
        app.processEvents()
        
        splash.update_progress(40, "Inicializando temas...")
        app.processEvents()
        
        splash.update_progress(60, "Preparando interfaz...")
        
        # Crear ventana principal (pero no mostrar aún)
        main_window = MainWindow()
        
        splash.update_progress(80, "Configurando componentes...")
        app.processEvents()
        
        splash.update_progress(100, "¡Listo!")
        app.processEvents()
        
        logger.info("Componentes cargados exitosamente")
        
        # Conectar señal de splash para mostrar ventana principal
        def show_main_window():
            splash.close()
            main_window.show()
            logger.info("Ventana principal mostrada")
        
        splash.loading_complete.connect(show_main_window)
        
    else:
        # Sin splash, mostrar ventana directamente
        logger.info("Splash screen deshabilitado, mostrando ventana principal...")
        main_window = MainWindow()
        main_window.show()
    
    logger.info("Aplicación lista para usar")
    logger.separador()
    
    # === EJECUTAR APLICACIÓN ===
    try:
        exit_code = app.exec()
        logger.info(f"Aplicación finalizada con código: {exit_code}")
        
        # Finalizar logging
        logger.finalizar("MatrixMAE cerrado correctamente")
        
        sys.exit(exit_code)
        
    except Exception as e:
        logger.error(f"Error crítico en la aplicación: {str(e)}", exc_info=True)
        logger.finalizar("MatrixMAE cerrado con errores")
        sys.exit(1)


if __name__ == "__main__":
    main()