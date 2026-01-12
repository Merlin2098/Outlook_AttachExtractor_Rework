
import sys
import os

# Inicializar COM para Outlook
try:
    import pythoncom
    pythoncom.CoInitialize()
except Exception as e:
    print(f"Warning: No se pudo inicializar COM: {e}")

# Limpiar cache de win32com si existe
try:
    import win32com
    gen_path = win32com.__gen_path__
    if os.path.exists(gen_path):
        import shutil
        shutil.rmtree(gen_path, ignore_errors=True)
except:
    pass
