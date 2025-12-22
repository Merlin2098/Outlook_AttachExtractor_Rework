# ui/splash_screen.py
"""
Splash screen de inicio para OutlookExtractor.
Muestra logo, versión y barra de progreso durante la carga.
"""

from PySide6.QtWidgets import QSplashScreen, QProgressBar, QLabel
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QPixmap, QPainter, QColor, QFont, QLinearGradient
from pathlib import Path


class SplashScreen(QSplashScreen):
    """
    Pantalla de inicio con logo, versión y progreso.
    
    Signals:
        loading_complete: Emitido cuando termina la carga
    """
    
    loading_complete = Signal()
    
    def __init__(self, icon_path: str = None):
        """
        Inicializa el splash screen.
        
        Args:
            icon_path: Ruta al icono de la aplicación (opcional)
        """
        # Dimensiones del splash
        self.splash_width = 500
        self.splash_height = 300
        
        # Crear pixmap para el splash
        pixmap = self._create_splash_pixmap(icon_path)
        super().__init__(pixmap, Qt.WindowType.WindowStaysOnTopHint)
        
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        
        self._setup_widgets()
        self._current_progress = 0
    
    def _create_splash_pixmap(self, icon_path: str = None) -> QPixmap:
        """
        Crea el pixmap del splash con gradiente y logo.
        
        Args:
            icon_path: Ruta al icono
            
        Returns:
            QPixmap configurado
        """
        pixmap = QPixmap(self.splash_width, self.splash_height)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Fondo con gradiente corporativo
        gradient = QLinearGradient(0, 0, 0, self.splash_height)
        gradient.setColorAt(0, QColor("#16A085"))  # Verde corporativo
        gradient.setColorAt(1, QColor("#0E6655"))  # Verde oscuro
        
        painter.setBrush(gradient)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, self.splash_width, self.splash_height, 15, 15)
        
        # Logo/Icono (si existe)
        if icon_path and Path(icon_path).exists():
            try:
                logo = QPixmap(icon_path).scaled(
                    100, 100,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                logo_x = (self.splash_width - 100) // 2
                painter.drawPixmap(logo_x, 40, logo)
            except Exception as e:
                print(f"⚠️ No se pudo cargar el icono: {e}")
        
        # Título
        painter.setPen(QColor("#FFFFFF"))
        font_title = QFont("Segoe UI", 24, QFont.Weight.Bold)
        painter.setFont(font_title)
        painter.drawText(
            0, 160, self.splash_width, 40,
            Qt.AlignmentFlag.AlignCenter,
            "OutlookExtractor"
        )
        
        # Subtítulo
        font_subtitle = QFont("Segoe UI", 12)
        painter.setFont(font_subtitle)
        painter.drawText(
            0, 195, self.splash_width, 30,
            Qt.AlignmentFlag.AlignCenter,
            "Gestor Automatizado de Correos"
        )
        
        # Versión
        font_version = QFont("Segoe UI", 9)
        painter.setFont(font_version)
        painter.drawText(
            0, 225, self.splash_width, 20,
            Qt.AlignmentFlag.AlignCenter,
            "v1.0.0 - PySide6"
        )
        
        painter.end()
        return pixmap
    
    def _setup_widgets(self):
        """
        Configura widgets sobre el splash usando posicionamiento manual.
        QSplashScreen NO soporta layouts - usar setGeometry()
        """
        # === BARRA DE PROGRESO ===
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setMaximum(100)
        
        # Posicionar barra de progreso
        bar_width = 400
        bar_height = 8
        bar_x = (self.splash_width - bar_width) // 2
        bar_y = self.splash_height - 50
        
        self.progress_bar.setGeometry(bar_x, bar_y, bar_width, bar_height)
        
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: rgba(255, 255, 255, 0.3);
                border: none;
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background-color: #FFFFFF;
                border-radius: 4px;
            }
        """)
        
        # === LABEL DE ESTADO ===
        self.status_label = QLabel("Inicializando...", self)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Posicionar label de estado
        label_width = 400
        label_height = 20
        label_x = (self.splash_width - label_width) // 2
        label_y = bar_y - 30  # 30px arriba de la barra
        
        self.status_label.setGeometry(label_x, label_y, label_width, label_height)
        
        self.status_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 11px;
                font-weight: bold;
                background-color: transparent;
            }
        """)
    
    def update_progress(self, value: int, message: str = ""):
        """
        Actualiza progreso y mensaje.
        
        Args:
            value: Valor de progreso (0-100)
            message: Mensaje de estado
        """
        self._current_progress = value
        self.progress_bar.setValue(value)
        
        if message:
            self.status_label.setText(message)
        
        # Procesar eventos para actualizar UI
        from PySide6.QtWidgets import QApplication
        QApplication.processEvents()
        
        # Si llegó a 100%, emitir señal con delay
        if value >= 100:
            QTimer.singleShot(500, self.loading_complete.emit)
    
    def simulate_loading(self, duration_ms: int = 2000):
        """
        Simula carga progresiva para testing.
        
        Args:
            duration_ms: Duración total en milisegundos
        """
        steps = [
            (20, "Cargando configuración..."),
            (40, "Inicializando temas..."),
            (60, "Conectando con Outlook..."),
            (80, "Preparando interfaz..."),
            (100, "¡Listo!")
        ]
        
        interval = duration_ms // len(steps)
        
        for i, (progress, msg) in enumerate(steps):
            QTimer.singleShot(
                i * interval,
                lambda p=progress, m=msg: self.update_progress(p, m)
            )


# Testing del splash screen
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication, QMainWindow
    
    app = QApplication(sys.argv)
    
    # Crear splash
    splash = SplashScreen()
    splash.show()
    
    # Simular carga
    splash.simulate_loading(3000)
    
    # Crear ventana principal (simulada)
    def show_main_window():
        main_window = QMainWindow()
        main_window.setWindowTitle("OutlookExtractor")
        main_window.resize(800, 600)
        main_window.show()
        splash.close()
    
    # Conectar señal
    splash.loading_complete.connect(show_main_window)
    
    sys.exit(app.exec())