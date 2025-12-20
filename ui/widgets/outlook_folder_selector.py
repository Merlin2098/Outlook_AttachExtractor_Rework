# ui/widgets/outlook_folder_selector.py
"""
Widget para seleccionar carpeta de Outlook con diálogo de navegación.
"""

import win32com.client
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLineEdit, QPushButton,
    QDialog, QVBoxLayout, QTreeWidget, QTreeWidgetItem,
    QLabel, QMessageBox, QApplication
)
from PySide6.QtCore import Qt, Signal
from .base_widget import BaseWidget


class OutlookFolderSelector(BaseWidget):
    """
    Widget para seleccionar carpeta de Outlook.
    
    Signals:
        folder_changed: Emitido cuando cambia la carpeta (str)
    """
    
    folder_changed = Signal(str)
    
    def __init__(self, placeholder: str = "Selecciona bandeja de Outlook...", 
                 button_text: str = "📧 Explorar", parent=None):
        """
        Args:
            placeholder: Texto placeholder
            button_text: Texto del botón
            parent: Widget padre
        """
        self.placeholder = placeholder
        self.button_text = button_text
        super().__init__(parent)
    
    def _setup_ui(self):
        """Construye la interfaz del selector"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Campo de texto
        self.folder_input = QLineEdit()
        self.folder_input.setPlaceholderText(self.placeholder)
        self.folder_input.setReadOnly(True)
        
        # Botón explorar
        self.browse_btn = QPushButton(self.button_text)
        self.browse_btn.clicked.connect(self._select_outlook_folder)
        self.browse_btn.setMinimumWidth(150)
        
        layout.addWidget(self.folder_input, stretch=1)
        layout.addWidget(self.browse_btn)
    
    def _select_outlook_folder(self):
        """Abre diálogo de selección de carpeta Outlook"""
        try:
            # Conectar con Outlook
            outlook = win32com.client.Dispatch("Outlook.Application")
            namespace = outlook.GetNamespace("MAPI")
            
            # Abrir diálogo
            dialog = OutlookFolderDialog(self, namespace)
            
            if dialog.exec() == QDialog.DialogCode.Accepted:
                folder = dialog.get_selected_folder()
                if folder:
                    self.folder_input.setText(folder)
                    self.folder_changed.emit(folder)
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo conectar con Outlook:\n{str(e)}"
            )
    
    def get_folder(self) -> str:
        """Obtiene la carpeta seleccionada"""
        return self.folder_input.text().strip()
    
    def set_folder(self, folder_path: str):
        """Establece la carpeta programáticamente"""
        self.folder_input.setText(folder_path)
    
    def clear(self):
        """Limpia el campo"""
        self.folder_input.clear()


class OutlookFolderDialog(QDialog):
    """
    Diálogo para navegar y seleccionar carpetas de Outlook.
    Implementa lazy loading para rendimiento.
    """
    
    def __init__(self, parent, namespace):
        super().__init__(parent)
        self.namespace = namespace
        self.selected_folder = None
        
        # Cache para lazy loading
        self.loaded_folders = set()
        self.outlook_folders_map = {}  # item_id -> outlook_folder
        
        self._setup_ui()
        self._load_root_folders()
    
    def _setup_ui(self):
        """Configura la interfaz del diálogo"""
        self.setWindowTitle("Seleccionar Bandeja de Outlook")
        self.setMinimumSize(900, 550)
        
        layout = QVBoxLayout()
        
        # Instrucciones
        info_label = QLabel(
            "⚠️ <b>Importante:</b> Navega hasta la carpeta exacta donde están los correos<br>"
            "💡 <b>Tip:</b> Haz clic en el ➕ para expandir carpetas<br>"
            "⚡ <b>Carga rápida:</b> Las subcarpetas se cargan al expandir (lazy loading)"
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Árbol de carpetas
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Carpeta", "Ruta completa"])
        self.tree.setColumnWidth(0, 350)
        self.tree.setColumnWidth(1, 500)
        
        # Conectar eventos
        self.tree.itemDoubleClicked.connect(self._on_accept)
        self.tree.itemClicked.connect(self._on_item_clicked)
        self.tree.itemExpanded.connect(self._load_subfolders_on_demand)
        
        layout.addWidget(self.tree)
        
        # Label de ruta seleccionada
        self.path_label = QLabel("📍 Ruta seleccionada: (ninguna)")
        self.path_label.setWordWrap(True)
        self.path_label.setStyleSheet(
            "padding: 8px; "
            "background-color: #e8f4f8; "
            "border: 1px solid #16A085; "
            "border-radius: 4px; "
            "font-family: 'Consolas', 'Courier New', monospace; "
            "font-size: 11px;"
        )
        layout.addWidget(self.path_label)
        
        # Botones
        btn_layout = QHBoxLayout()
        
        accept_btn = QPushButton("✔ Aceptar")
        accept_btn.clicked.connect(self._on_accept)
        accept_btn.setMinimumHeight(35)
        
        cancel_btn = QPushButton("✗ Cancelar")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setMinimumHeight(35)
        
        btn_layout.addStretch()
        btn_layout.addWidget(accept_btn)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def _load_root_folders(self):
        """Carga solo las cuentas principales (nivel raíz)"""
        try:
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            
            for folder in self.namespace.Folders:
                account_name = str(folder.Name)
                
                # Crear item de cuenta
                item = QTreeWidgetItem([f"📧 {account_name}", account_name])
                item.setData(0, Qt.ItemDataRole.UserRole, account_name)
                
                # Tooltips
                item.setToolTip(0, account_name)
                item.setToolTip(1, account_name)
                
                # Guardar referencia al objeto Outlook
                item_id = id(item)
                self.outlook_folders_map[item_id] = folder
                item.setData(0, Qt.ItemDataRole.UserRole + 1, item_id)
                
                # Agregar dummy child si tiene subcarpetas
                try:
                    if folder.Folders.Count > 0:
                        dummy = QTreeWidgetItem(["⏳ Cargando...", ""])
                        item.addChild(dummy)
                except:
                    pass
                
                self.tree.addTopLevelItem(item)
            
            QApplication.restoreOverrideCursor()
            
        except Exception as e:
            QApplication.restoreOverrideCursor()
            QMessageBox.critical(self, "Error", f"Error cargando bandejas: {str(e)}")
    
    def _load_subfolders_on_demand(self, item):
        """Lazy loading: carga subcarpetas solo al expandir"""
        item_id = item.data(0, Qt.ItemDataRole.UserRole + 1)
        
        # Ya fue cargado
        if item_id in self.loaded_folders:
            return
        
        # Marcar como cargado
        self.loaded_folders.add(item_id)
        
        # Obtener objeto Outlook
        outlook_folder = self.outlook_folders_map.get(item_id)
        if not outlook_folder:
            return
        
        try:
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            
            # Remover dummy items
            while item.childCount() > 0:
                item.removeChild(item.child(0))
            
            # Obtener ruta padre
            ruta_padre = item.data(0, Qt.ItemDataRole.UserRole)
            
            # Cargar subcarpetas
            try:
                for subfolder in outlook_folder.Folders:
                    nombre_sub = str(subfolder.Name)
                    ruta_completa = f"{ruta_padre}\\{nombre_sub}"
                    
                    # Crear item
                    sub_item = QTreeWidgetItem([f"📁 {nombre_sub}", ruta_completa])
                    sub_item.setData(0, Qt.ItemDataRole.UserRole, ruta_completa)
                    
                    # Tooltips
                    sub_item.setToolTip(0, ruta_completa)
                    sub_item.setToolTip(1, ruta_completa)
                    
                    # Guardar referencia
                    sub_id = id(sub_item)
                    self.outlook_folders_map[sub_id] = subfolder
                    sub_item.setData(0, Qt.ItemDataRole.UserRole + 1, sub_id)
                    
                    # Agregar dummy si tiene subcarpetas
                    try:
                        if subfolder.Folders.Count > 0:
                            dummy = QTreeWidgetItem(["⏳ Cargando...", ""])
                            sub_item.addChild(dummy)
                    except:
                        pass
                    
                    item.addChild(sub_item)
            
            except Exception as e:
                print(f"Error cargando subcarpetas: {e}")
            
            QApplication.restoreOverrideCursor()
            
        except Exception as e:
            QApplication.restoreOverrideCursor()
            QMessageBox.warning(self, "Advertencia", f"Error cargando subcarpetas: {str(e)}")
    
    def _on_item_clicked(self, item, column):
        """Actualiza label con ruta seleccionada"""
        ruta = item.data(0, Qt.ItemDataRole.UserRole)
        if ruta:
            self.path_label.setText(f"📍 Ruta seleccionada: {ruta}")
    
    def _on_accept(self):
        """Acepta la selección"""
        current_item = self.tree.currentItem()
        if current_item:
            ruta = current_item.data(0, Qt.ItemDataRole.UserRole)
            if ruta and not ruta.startswith("⏳"):
                self.selected_folder = ruta
                self.accept()
            else:
                QMessageBox.warning(
                    self,
                    "Atención",
                    "Selecciona una carpeta válida (no un placeholder de carga)"
                )
        else:
            QMessageBox.warning(
                self,
                "Atención",
                "Selecciona una carpeta antes de aceptar"
            )
    
    def get_selected_folder(self) -> str:
        """Obtiene la carpeta seleccionada"""
        return self.selected_folder


# Exportar
__all__ = ['OutlookFolderSelector', 'OutlookFolderDialog']