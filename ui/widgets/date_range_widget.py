# ui/widgets/date_range_widget.py
"""
Widget reutilizable para selección de rango de fechas.
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QDateEdit, QSizePolicy
from PySide6.QtCore import QDate
from datetime import datetime
from .base_widget import BaseWidget


class DateRangeWidget(BaseWidget):
    """
    Widget para seleccionar rango de fechas (SIEMPRE ACTIVO).
    
    Características:
    - Selector de fecha inicio con calendario
    - Selector de fecha fin con calendario
    - Calendario popup
    - Sin checkbox - siempre habilitado
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def _setup_ui(self):
        """Construye la interfaz del selector de fechas"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Label "Desde:" SIN emoji
        label_from = QLabel("Desde:")
        label_from.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        
        # Selector de fecha inicio
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addDays(-30))  # 30 días atrás
        self.date_from.setDisplayFormat("dd/MM/yyyy")
        self.date_from.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.date_from.setMinimumWidth(130)
        
        # Label "Hasta:" SIN emoji
        label_to = QLabel("Hasta:")
        label_to.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        
        # Selector de fecha fin
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())  # Hoy
        self.date_to.setDisplayFormat("dd/MM/yyyy")
        self.date_to.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.date_to.setMinimumWidth(130)
        
        # Ensamblar layout
        layout.addWidget(label_from)
        layout.addWidget(self.date_from)
        layout.addWidget(label_to)
        layout.addWidget(self.date_to)
        layout.addStretch()
    
    def get_range(self):
        """
        Obtiene el rango de fechas seleccionado (SIEMPRE retorna fechas).
        
        Returns:
            tuple[datetime, datetime]: (fecha_inicio, fecha_fin)
        """
        # Convertir QDate a datetime.date
        date_from = self.date_from.date().toPython()
        date_to = self.date_to.date().toPython()
        
        # Convertir a datetime con horas completas del día
        # Desde: 00:00:00
        dt_from = datetime.combine(date_from, datetime.min.time())
        
        # Hasta: 23:59:59.999999
        dt_to = datetime.combine(date_to, datetime.max.time())
        
        return (dt_from, dt_to)
    
    def set_range(self, date_from: datetime = None, date_to: datetime = None):
        """
        Establece el rango de fechas programáticamente.
        
        Args:
            date_from: Fecha de inicio (datetime)
            date_to: Fecha de fin (datetime)
        """
        if date_from:
            qdate_from = QDate(date_from.year, date_from.month, date_from.day)
            self.date_from.setDate(qdate_from)
        
        if date_to:
            qdate_to = QDate(date_to.year, date_to.month, date_to.day)
            self.date_to.setDate(qdate_to)
    
    def is_enabled(self) -> bool:
        """
        Verifica si el filtro por fechas está habilitado.
        
        Returns:
            bool: Siempre True (ya no hay checkbox)
        """
        return True
    
    def clear(self):
        """Resetea el widget a valores por defecto"""
        self.date_from.setDate(QDate.currentDate().addDays(-30))
        self.date_to.setDate(QDate.currentDate())