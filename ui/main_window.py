# ui/main_window.py
"""
Ventana principal de MatrixMAE.
Orquesta tabs, menús y aplicación de temas.
"""

from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QStatusBar, QScrollArea,
    QMenuBar, QMessageBox, QApplication, QWidget
)
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QAction, QIcon
from pathlib import Path
import sys
import os

from config.config_manager import ConfigManager
from ui.theme_manager import ThemeManager
from ui.tabs import TabExtractor, TabClasificador


class MainWindow(QMainWindow):
    """
    Ventana principal de MatrixMAE.
    
    Características:
    - Tabs: Extractor y Clasificador con scroll area
    - Menú: Archivo, Temas, Ayuda
    - StatusBar con mensajes
    - Integración con ThemeManager
    - Aplica temas a TODA la aplicación (ventanas emergentes incluidas)
    """
    
    def __init__(self):
        super().__init__()
        
        self.config = ConfigManager()
        self.theme_manager = ThemeManager()
        
        self._setup_window()
        self._setup_menu()
        self._setup_tabs()
        self._setup_statusbar()
        self._connect_signals()
        
        # Aplicar tema inicial A TODA LA APLICACIÓN
        self._apply_current_theme()
    
    def _setup_window(self):
        """Configura propiedades de la ventana"""
        self.setWindowTitle("MatrixMAE - Gestor Automatizado de Correos")
        
        # Tamaño desde configuración
        width = self.config.get('ui.window.width', 1000)
        height = self.config.get('ui.window.height', 700)
        self.resize(width, height)
        
        # === CARGA DE ICONO MEJORADA ===
        # Determinar directorio base
        if getattr(sys, 'frozen', False):
            # Ejecutable compilado con PyInstaller
            base_dir = Path(sys._MEIPASS)
        else:
            # Desarrollo - directorio del proyecto
            base_dir = Path(__file__).parent.parent
        
        # Ruta al icono
        icon_path = base_dir / "config" / "app.ico"
        
        # Intentar cargar el icono
        if icon_path.exists():
            try:
                icon = QIcon(str(icon_path))
                if not icon.isNull():
                    self.setWindowIcon(icon)
                    # También establecer en QApplication para todas las ventanas
                    QApplication.instance().setWindowIcon(icon)
                    print(f"✅ Icono cargado: {icon_path}")
                else:
                    print(f"⚠️ Icono inválido (isNull): {icon_path}")
                    print("   Verifica que sea un archivo .ico válido")
            except Exception as e:
                print(f"❌ Error cargando icono: {e}")
        else:
            print(f"⚠️ Icono no encontrado: {icon_path}")
            print(f"   Directorio base: {base_dir}")
            print(f"   Ruta completa: {icon_path.absolute()}")
            
            # Intentar rutas alternativas
            alt_paths = [
                Path("config/app.ico"),
                Path("../config/app.ico"),
                Path("./config/app.ico")
            ]
            
            for alt_path in alt_paths:
                if alt_path.exists():
                    try:
                        icon = QIcon(str(alt_path))
                        if not icon.isNull():
                            self.setWindowIcon(icon)
                            QApplication.instance().setWindowIcon(icon)
                            print(f"✅ Icono cargado desde ruta alternativa: {alt_path.absolute()}")
                            break
                    except:
                        continue
    
    def _setup_menu(self):
        """Configura el menú superior"""
        menubar = self.menuBar()
        
        # === MENÚ ARCHIVO ===
        menu_archivo = menubar.addMenu("&Archivo")
        
        # Acción: Salir
        action_salir = QAction("&Salir", self)
        action_salir.setShortcut("Ctrl+Q")
        action_salir.setStatusTip("Salir de la aplicación")
        action_salir.triggered.connect(self.close)
        menu_archivo.addAction(action_salir)
        
        # === MENÚ TEMAS ===
        menu_temas = menubar.addMenu("&Temas")
        
        # Acción: Tema Claro
        self.action_tema_claro = QAction("Tema &Claro", self)
        self.action_tema_claro.setCheckable(True)
        self.action_tema_claro.setStatusTip("Aplicar tema claro")
        self.action_tema_claro.triggered.connect(lambda: self._cambiar_tema('light'))
        menu_temas.addAction(self.action_tema_claro)
        
        # Acción: Tema Oscuro
        self.action_tema_oscuro = QAction("Tema &Oscuro", self)
        self.action_tema_oscuro.setCheckable(True)
        self.action_tema_oscuro.setStatusTip("Aplicar tema oscuro")
        self.action_tema_oscuro.triggered.connect(lambda: self._cambiar_tema('dark'))
        menu_temas.addAction(self.action_tema_oscuro)
        
        # Marcar tema actual
        tema_actual = self.theme_manager._current_theme_name
        if tema_actual == 'light':
            self.action_tema_claro.setChecked(True)
        else:
            self.action_tema_oscuro.setChecked(True)
        
        # === MENÚ AYUDA ===
        menu_ayuda = menubar.addMenu("A&yuda")
        
        # Nota: "Acerca de" eliminado según requerimiento
    
    def _setup_tabs(self):
        """Configura el widget de tabs con scroll area"""
        # Crear tabs
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)
        
        self.tab_extractor = TabExtractor()
        self.tab_clasificador = TabClasificador()
        
        # Agregar tabs
        self.tabs.addTab(self.tab_extractor, "🔎 Extractor de Adjuntos")
        self.tabs.addTab(self.tab_clasificador, "📋 Clasificador de Documentos")
        
        # === AGREGAR SCROLL AREA ===
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.tabs)
        scroll_area.setWidgetResizable(True)  # Importante para que el contenido se ajuste
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Establecer scroll area como widget central
        self.setCentralWidget(scroll_area)
    
    def _setup_statusbar(self):
        """Configura la barra de estado"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Listo", 3000)
    
    def _connect_signals(self):
        """Conecta señales de los tabs con la ventana principal"""
        # Extractor
        self.tab_extractor.extraction_started.connect(self._on_extraction_started)
        self.tab_extractor.extraction_finished.connect(self._on_extraction_finished)
        self.tab_extractor.error_occurred.connect(self._on_tab_error)
        self.tab_extractor.status_changed.connect(self._on_status_message)
        
        # Clasificador
        self.tab_clasificador.classification_started.connect(self._on_classification_started)
        self.tab_clasificador.classification_finished.connect(self._on_classification_finished)
        self.tab_clasificador.error_occurred.connect(self._on_tab_error)
        self.tab_clasificador.status_changed.connect(self._on_status_message)
    
    def _cambiar_tema(self, tema: str):
        """
        Cambia el tema de la aplicación.
        
        Args:
            tema: 'light' o 'dark'
        """
        # Actualizar checks del menú
        self.action_tema_claro.setChecked(tema == 'light')
        self.action_tema_oscuro.setChecked(tema == 'dark')
        
        # Cambiar tema en ThemeManager (se guarda en config.json)
        self.theme_manager.set_theme(tema)
        
        # ✅ CRÍTICO: Re-aplicar stylesheet después del cambio
        self._apply_current_theme()
        
        # Mensaje en statusbar
        nombre_tema = "Claro" if tema == 'light' else "Oscuro"
        self.statusbar.showMessage(f"Tema cambiado a: {nombre_tema}", 3000)
    
    def _apply_current_theme(self):
        """
        Aplica el tema actual a TODA la aplicación.
        
        IMPORTANTE: Usa QApplication.instance().setStyleSheet() en lugar de 
        self.setStyleSheet() para que el tema se aplique a TODAS las ventanas,
        incluyendo diálogos emergentes (QFileDialog, QMessageBox, QMenu, etc.)
        """
        stylesheet = self.theme_manager.get_stylesheet()
        
        # ✅ Aplicar a QApplication (afecta TODA la app, incluidas ventanas emergentes)
        QApplication.instance().setStyleSheet(stylesheet)
        
        print(f"✅ Tema aplicado globalmente: {self.theme_manager.get_current_theme()}")
    
    # === SLOTS PARA SEÑALES DE TABS ===
    
    @Slot(dict)
    def _on_extraction_started(self, params: dict):
        """Handler cuando inicia extracción"""
        self.statusbar.showMessage("Extracción en proceso...", 0)
    
    @Slot(dict)
    def _on_extraction_finished(self, stats: dict):
        """Handler cuando termina extracción"""
        adjuntos = stats.get('adjuntos_descargados', 0)
        self.statusbar.showMessage(
            f"✅ Extracción completada: {adjuntos} adjuntos descargados",
            5000
        )
        
        # Notificación sonora si está habilitada
        if self.config.get('app.beep_on_complete', True):
            self._beep()
    
    @Slot(dict)
    def _on_classification_started(self, params: dict):
        """Handler cuando inicia clasificación"""
        self.statusbar.showMessage("Clasificación en proceso...", 0)
    
    @Slot(dict)
    def _on_classification_finished(self, stats: dict):
        """Handler cuando termina clasificación"""
        firmados = stats.get('firmados', 0)
        sin_firmar = stats.get('sin_firmar', 0)
        self.statusbar.showMessage(
            f"✅ Clasificación completada: {firmados} firmados, {sin_firmar} sin firmar",
            5000
        )
        
        # Notificación sonora
        if self.config.get('app.beep_on_complete', True):
            self._beep()
    
    @Slot(str)
    def _on_tab_error(self, error_msg: str):
        """Handler para errores de tabs"""
        self.statusbar.showMessage(f"❌ {error_msg}", 5000)
        
        # Mostrar diálogo de error
        QMessageBox.critical(self, "Error", error_msg)
    
    @Slot(str)
    def _on_status_message(self, message: str):
        """Handler para mensajes de estado de tabs"""
        self.statusbar.showMessage(message, 3000)
    
    def _beep(self):
        """Emite un beep de notificación"""
        try:
            import winsound
            winsound.MessageBeep(winsound.MB_OK)
        except:
            pass
    
    def closeEvent(self, event):
        """Override del evento de cierre"""
        # Guardar tamaño de ventana
        self.config.set('ui.window.width', self.width())
        self.config.set('ui.window.height', self.height())
        
        # Aceptar cierre
        event.accept()


# Exportar
__all__ = ['MainWindow']