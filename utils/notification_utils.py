# utils/notification_utils.py
"""
Utilidades para notificaciones visuales y sonoras.
Incluye sonidos del sistema y parpadeo de ventana en taskbar.
"""

import ctypes
from ctypes import wintypes


# Constantes para FlashWindowEx
FLASHW_STOP = 0
FLASHW_CAPTION = 0x00000001
FLASHW_TRAY = 0x00000002
FLASHW_ALL = FLASHW_CAPTION | FLASHW_TRAY
FLASHW_TIMER = 0x00000004
FLASHW_TIMERNOFG = 0x0000000C


class FLASHWINFO(ctypes.Structure):
    """Estructura para FlashWindowEx de Windows API"""
    _fields_ = [
        ('cbSize', wintypes.UINT),
        ('hwnd', wintypes.HANDLE),
        ('dwFlags', wintypes.DWORD),
        ('uCount', wintypes.UINT),
        ('dwTimeout', wintypes.DWORD)
    ]


def play_completion_sound() -> bool:
    """
    Reproduce sonido de completación del sistema.
    
    Intenta reproducir un sonido de notificación usando winsound.
    Si falla (usuario tiene sonidos silenciados), retorna False.
    
    Returns:
        bool: True si se reprodujo el sonido
    """
    try:
        import winsound
        winsound.MessageBeep(winsound.MB_ICONASTERISK)
        return True
    except Exception as e:
        print(f"⚠️ No se pudo reproducir sonido: {e}")
        return False


def flash_window(hwnd: int, count: int = 3, flash_rate: int = 500) -> bool:
    """
    Hace parpadear la ventana en el taskbar para llamar atención del usuario.
    
    Args:
        hwnd: Handle de la ventana (obtener con QWidget.winId())
        count: Número de parpadeos (0 = hasta que usuario active ventana)
        flash_rate: Velocidad de parpadeo en milisegundos
    
    Returns:
        bool: True si se aplicó correctamente
    """
    try:
        # Configurar estructura FLASHWINFO
        flash_info = FLASHWINFO()
        flash_info.cbSize = ctypes.sizeof(FLASHWINFO)
        flash_info.hwnd = hwnd
        flash_info.dwFlags = FLASHW_ALL | FLASHW_TIMERNOFG
        flash_info.uCount = count
        flash_info.dwTimeout = flash_rate
        
        # Llamar a FlashWindowEx
        result = ctypes.windll.user32.FlashWindowEx(ctypes.byref(flash_info))
        return result != 0
        
    except Exception as e:
        print(f"⚠️ Error al hacer parpadear ventana: {e}")
        return False


def stop_flashing(hwnd: int) -> bool:
    """
    Detiene el parpadeo de una ventana.
    
    Args:
        hwnd: Handle de la ventana
    
    Returns:
        bool: True si se detuvo correctamente
    """
    try:
        flash_info = FLASHWINFO()
        flash_info.cbSize = ctypes.sizeof(FLASHWINFO)
        flash_info.hwnd = hwnd
        flash_info.dwFlags = FLASHW_STOP
        flash_info.uCount = 0
        flash_info.dwTimeout = 0
        
        result = ctypes.windll.user32.FlashWindowEx(ctypes.byref(flash_info))
        return result != 0
        
    except Exception as e:
        print(f"⚠️ Error al detener parpadeo: {e}")
        return False


def is_window_foreground(hwnd: int) -> bool:
    """
    Verifica si una ventana tiene el foco actual.
    
    Args:
        hwnd: Handle de la ventana
    
    Returns:
        bool: True si la ventana está en primer plano
    """
    try:
        foreground_hwnd = ctypes.windll.user32.GetForegroundWindow()
        return foreground_hwnd == hwnd
    except Exception as e:
        print(f"⚠️ Error al verificar ventana en primer plano: {e}")
        return False


def notify_completion(hwnd: int, force_flash: bool = False) -> None:
    """
    Notifica finalización de proceso con sonido y parpadeo (si aplica).
    
    Args:
        hwnd: Handle de la ventana principal
        force_flash: Si True, hace parpadear incluso si ventana tiene foco
    """
    # Reproducir sonido
    play_completion_sound()
    
    # Parpadear solo si ventana NO tiene foco o force_flash=True
    if force_flash or not is_window_foreground(hwnd):
        flash_window(hwnd, count=3, flash_rate=500)


# Exportar
__all__ = [
    'play_completion_sound',
    'flash_window',
    'stop_flashing',
    'is_window_foreground',
    'notify_completion'
]