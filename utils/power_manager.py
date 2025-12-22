# utils/power_manager.py
"""
Gestor de energía del sistema para prevenir suspensión durante procesos largos.
Utiliza Windows API para controlar el estado de suspensión y bloqueo de pantalla.
"""

import ctypes
from typing import Optional

# Constantes de Windows API para SetThreadExecutionState
ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002
ES_AWAYMODE_REQUIRED = 0x00000040


class PowerManager:
    """
    Gestor de energía del sistema.
    
    Previene:
    - Suspensión automática del sistema
    - Apagado de pantalla por inactividad
    - Bloqueo automático de pantalla
    """
    
    def __init__(self):
        self._previous_state: Optional[int] = None
        self._is_prevented = False
    
    def prevent_sleep(self) -> bool:
        """
        Previene suspensión del sistema y apagado de pantalla.
        
        Returns:
            bool: True si se aplicó correctamente
        """
        if self._is_prevented:
            return True
        
        try:
            # Combinar flags para prevenir suspensión y apagado de pantalla
            flags = ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
            
            # Aplicar configuración
            self._previous_state = ctypes.windll.kernel32.SetThreadExecutionState(flags)
            self._is_prevented = True
            
            return True
            
        except Exception as e:
            print(f"⚠️ Error al prevenir suspensión: {e}")
            return False
    
    def allow_sleep(self) -> bool:
        """
        Restaura comportamiento normal de suspensión.
        
        Returns:
            bool: True si se restauró correctamente
        """
        if not self._is_prevented:
            return True
        
        try:
            # Restaurar estado normal (ES_CONTINUOUS solo)
            ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)
            self._is_prevented = False
            self._previous_state = None
            
            return True
            
        except Exception as e:
            print(f"⚠️ Error al restaurar suspensión: {e}")
            return False
    
    def is_prevented(self) -> bool:
        """
        Verifica si la suspensión está actualmente prevenida.
        
        Returns:
            bool: True si está prevenida
        """
        return self._is_prevented


# Funciones de conveniencia para uso directo
def prevent_sleep_mode() -> bool:
    """
    Previene suspensión del sistema (función de conveniencia).
    
    Returns:
        bool: True si se aplicó correctamente
    """
    try:
        flags = ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
        ctypes.windll.kernel32.SetThreadExecutionState(flags)
        return True
    except Exception as e:
        print(f"⚠️ Error al prevenir suspensión: {e}")
        return False


def allow_sleep_mode() -> bool:
    """
    Restaura comportamiento normal de suspensión (función de conveniencia).
    
    Returns:
        bool: True si se restauró correctamente
    """
    try:
        ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)
        return True
    except Exception as e:
        print(f"⚠️ Error al restaurar suspensión: {e}")
        return False


# Exportar
__all__ = ['PowerManager', 'prevent_sleep_mode', 'allow_sleep_mode']