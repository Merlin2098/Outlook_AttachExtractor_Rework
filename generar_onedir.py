"""
Script de Generación de Ejecutable Onedir
Proyecto: MatrixMAE (Gestor Automatizado de Correos)
Genera un ejecutable Windows con carpeta distribuible

Autor: Richi
Fecha: 2025
Framework: PySide6 con integración Outlook COM
"""

import os
import sys
import pkg_resources
import subprocess
import shutil
from pathlib import Path
import time
import threading

# ==========================================================
# CONFIGURACIÓN
# ==========================================================
NOMBRE_EXE = "OutlookExtractor.exe"
MAIN_SCRIPT = "main.py"

DIST_PATH = "dist"
BUILD_PATH = "build"
SPEC_PATH = "spec"

# Exclusiones de módulos innecesarios para reducir tamaño
EXCLUSIONES = [
    "pip", "ensurepip", "test", "tkinter.test",
    "pytest", "pytest_cov", "coverage", "notebook",
    "IPython", "jupyter", "matplotlib", "scipy",
    "numpy.testing", "pandas.tests"
]

# ==========================================================
# VALIDAR ENTORNO VIRTUAL
# ==========================================================
def validar_entorno_virtual():
    """Verifica que se esté ejecutando dentro de un entorno virtual"""
    print("=" * 60)
    print("🔍 VALIDACIÓN DE ENTORNO VIRTUAL")
    print("=" * 60)

    if sys.prefix == sys.base_prefix:
        print("❌ ERROR: No estás dentro de un entorno virtual (venv).")
        print("   Activa uno antes de continuar.")
        print("   Ejemplo Windows: venv\\Scripts\\activate")
        sys.exit(1)

    print(f"✅ Entorno virtual detectado: {sys.prefix}\n")

    try:
        paquetes = sorted([(pkg.key, pkg.version) for pkg in pkg_resources.working_set])
        print(f"📦 Librerías instaladas ({len(paquetes)}):")
        for nombre, version in paquetes:
            flag = "🧹 (excluir)" if nombre in EXCLUSIONES else "✅"
            print(f"   {flag} {nombre:<25} {version}")
    except Exception:
        print("⚠️ No se pudo listar paquetes con pkg_resources (no crítico).")
    print("\n")

# ==========================================================
# CONFIRMACIÓN MANUAL
# ==========================================================
def confirmar_ejecucion():
    """Solicita confirmación del usuario antes de continuar"""
    print("=" * 60)
    print("⚠️  CONFIRMACIÓN DE EJECUCIÓN")
    print("=" * 60)
    print("Este proceso generará un ejecutable Windows onedir.")
    print("Se incluirán todos los recursos, temas y configuraciones.\n")
    
    respuesta = input("¿Deseas generar el ejecutable ahora? (S/N): ").strip().lower()

    if respuesta not in ("s", "si", "sí"):
        print("\n🛑 Proceso cancelado por el usuario.")
        sys.exit(0)

    print("\n✅ Confirmado. Continuando con la generación...\n")

# ==========================================================
# LIMPIAR BUILDS ANTERIORES
# ==========================================================
def limpiar_builds():
    """Elimina carpetas de builds anteriores"""
    print("🧹 Limpiando builds anteriores...")
    for carpeta in [DIST_PATH, BUILD_PATH, SPEC_PATH]:
        if os.path.exists(carpeta):
            try:
                shutil.rmtree(carpeta)
                print(f"   ✅ Eliminado: {carpeta}")
            except Exception as e:
                print(f"   ⚠️  No se pudo eliminar {carpeta}: {e}")
    print()

# ==========================================================
# CONSTRUIR COMANDO PYINSTALLER
# ==========================================================
def construir_comando():
    """Construye el comando completo de PyInstaller"""
    base_dir = Path.cwd()

    comando = [
        sys.executable, "-m", "PyInstaller",
        "--onedir",              # Modo directorio (no onefile)
        "--windowed",            # Sin consola (GUI)
        "--clean",               # Limpiar cache
        "--log-level", "WARN",   # Solo warnings y errores
        "--distpath", DIST_PATH,
        "--workpath", BUILD_PATH,
        "--specpath", SPEC_PATH,
        "--name", NOMBRE_EXE.replace(".exe", ""),
        "--noconfirm",           # No preguntar confirmar sobreescritura
    ]

    # ======================================================
    # PATHS: Agregar rutas para imports
    # ======================================================
    comando += ["--paths", str(base_dir)]

    # Agregar carpetas específicas del proyecto
    for carpeta in ["ui", "ui/tabs", "ui/widgets", "core", "utils", "workers", "config"]:
        ruta = base_dir / carpeta
        if ruta.exists():
            comando += ["--paths", str(ruta)]

    # ======================================================
    # HIDDEN IMPORTS: Dependencias no detectadas automáticamente
    # ======================================================
    hidden_imports = [
        # PySide6 core
        "PySide6.QtCore",
        "PySide6.QtGui", 
        "PySide6.QtWidgets",
        
        # Outlook COM - CRÍTICO para MatrixMAE
        "win32com",
        "win32com.client",
        "win32com.client.gencache",
        "win32com.client.makepy",
        "pythoncom",
        "pywintypes",
        "winerror",
        
        # Excel y datos (según requirements.txt)
        "openpyxl",
        "openpyxl.styles",
        "openpyxl.utils",
        "xlsxwriter",
        "xlsxwriter.workbook",
        "xlsxwriter.worksheet",
        "polars",
        "polars.datatypes",
        "polars.io",
        
        # Fechas y utilidades
        "dateutil",
        "dateutil.parser",
        "dateutil.tz",
        
        # Logging
        "colorlog",
        "colorlog.formatter",
        
        # Threading y sistema
        "threading",
        "queue",
        "winsound",
        
        # Utilidades estándar
        "re",
        "pathlib",
        "json",
        "datetime",
        "shutil",
        "logging",
        "logging.handlers",
        
        # Módulos del proyecto - UI
        "ui.main_window",
        "ui.splash_screen",
        "ui.theme_manager",
        "ui.tabs.base_tab",
        "ui.tabs.tab_extractor",
        "ui.tabs.tab_clasificador",
        
        # Módulos del proyecto - Widgets
        "ui.widgets.base_widget",
        "ui.widgets.author_info_widget",
        "ui.widgets.date_range_widget",
        "ui.widgets.folder_selector_widget",
        "ui.widgets.outlook_folder_selector",
        "ui.widgets.phrase_search_widget",
        "ui.widgets.progress_widget",
        "ui.widgets.theme_toggle_widget",
        
        # Módulos del proyecto - Workers
        "workers.base_worker",
        "workers.extractor_worker",
        "workers.classifier_worker",
        
        # Módulos del proyecto - Core
        "core.backend_base",
        "core.email_extractor",
        "core.sign_classifier",
        
        # Módulos del proyecto - Utils
        "utils.logger",
        "utils.date_handler",
        "utils.notification_utils",
        "utils.power_manager",
        "utils.audit_mails",
        
        # Módulos del proyecto - Config
        "config.config_manager",
    ]
    
    for imp in hidden_imports:
        comando += ["--hidden-import", imp]

    # ======================================================
    # EXCLUSIONES: Módulos innecesarios
    # ======================================================
    for excl in EXCLUSIONES:
        comando += ["--exclude-module", excl]

    # ======================================================
    # ICONO DE LA APLICACIÓN
    # ======================================================
    ico_path = base_dir / "config" / "app.ico"
    if ico_path.exists():
        comando += ["--icon", str(ico_path)]
        print(f"   ✅ Icono encontrado: {ico_path}")
    else:
        print(f"   ⚠️  Advertencia: No se encontró el icono en {ico_path}")
    
    # ======================================================
    # RUNTIME HOOKS (para COM y pythoncom)
    # ======================================================
    print("\n🔧 Configurando runtime hooks...")
    
    # Hook para inicializar COM en el ejecutable
    runtime_hook_path = base_dir / "runtime_hook_com.py"
    runtime_hook_content = '''
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
'''
    
    with open(runtime_hook_path, "w", encoding="utf-8") as f:
        f.write(runtime_hook_content)
    
    comando += ["--runtime-hook", str(runtime_hook_path)]
    print(f"   ✅ Runtime hook creado: {runtime_hook_path}")
    
    # ======================================================
    # DATA FILES: Recursos y configuraciones
    # ======================================================
    print("\n📁 Agregando recursos...")
    
    # Carpeta config completa (temas, configuraciones, icono)
    config_path = base_dir / "config"
    if config_path.exists():
        comando += ["--add-data", f"{config_path}{os.pathsep}config"]
        print(f"   ✅ Carpeta config agregada")
    
    # ======================================================
    # COLLECT ALL: Subpaquetes completos
    # ======================================================
    # Recolectar todos los módulos de win32com
    comando += ["--collect-all", "win32com"]
    comando += ["--collect-all", "pythoncom"]
    comando += ["--collect-all", "pywintypes"]
    
    # Recolectar polars completamente
    comando += ["--collect-all", "polars"]
    
    print(f"   ✅ Módulos COM y Polars recolectados completamente")
    
    # Script principal
    comando.append(MAIN_SCRIPT)
    
    return comando

# ==========================================================
# GENERAR EJECUTABLE
# ==========================================================
def generar_exe():
    """Genera el ejecutable usando PyInstaller"""
    limpiar_builds()
    
    cmd = construir_comando()
    
    print("\n" + "=" * 60)
    print("🔨 COMANDO PYINSTALLER")
    print("=" * 60)
    print("─" * 60)
    print(" ".join(cmd))
    print("─" * 60 + "\n")
    
    # Ejecutar PyInstaller con captura de salida en tiempo real
    print("🔨 Ejecutando PyInstaller...\n")
    
    # Fases estimadas del proceso
    fases = [
        ("📦 Analizando dependencias", 0, 15),
        ("🔍 Detectando módulos COM", 15, 30),
        ("📚 Recopilando archivos", 30, 50),
        ("⚙️  Compilando ejecutable", 50, 75),
        ("📁 Empaquetando recursos", 75, 90),
        ("✨ Finalizando bundle", 90, 100),
    ]
    
    # Variable para controlar el progreso
    progreso_actual = [0]
    proceso_completado = [False]
    
    def mostrar_progreso():
        """Muestra una barra de progreso animada"""
        simbolos = ['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷']
        idx = 0
        fase_actual = 0
        
        while not proceso_completado[0]:
            # Determinar fase actual basada en progreso
            for i, (nombre, inicio, fin) in enumerate(fases):
                if inicio <= progreso_actual[0] < fin:
                    fase_actual = i
                    break
            
            fase_nombre = fases[fase_actual][0]
            porcentaje = progreso_actual[0]
            
            # Construir barra
            barra_len = 40
            lleno = int(barra_len * porcentaje / 100)
            vacio = barra_len - lleno
            barra = "█" * lleno + "░" * vacio
            
            # Mostrar con animación
            print(f"\r{simbolos[idx]} {fase_nombre:<35} [{barra}] {porcentaje:3d}%", end="", flush=True)
            
            idx = (idx + 1) % len(simbolos)
            time.sleep(0.1)
        
        # Barra completa al finalizar
        print(f"\r✅ Generación completada          [{'█' * 40}] 100%")
    
    def actualizar_progreso():
        """Simula el progreso basado en tiempo estimado"""
        tiempo_total = 60
        intervalos = 100
        tiempo_por_intervalo = tiempo_total / intervalos
        
        for i in range(intervalos + 1):
            if proceso_completado[0]:
                break
            progreso_actual[0] = i
            time.sleep(tiempo_por_intervalo)
    
    # Iniciar thread de progreso
    thread_progreso = threading.Thread(target=mostrar_progreso, daemon=True)
    thread_actualizar = threading.Thread(target=actualizar_progreso, daemon=True)
    
    thread_progreso.start()
    thread_actualizar.start()
    
    # Ejecutar PyInstaller
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Marcar como completado
    proceso_completado[0] = True
    progreso_actual[0] = 100
    
    # Esperar a que termine la animación
    time.sleep(0.5)
    
    print("\n\n" + "=" * 60)
    if result.returncode == 0:
        carpeta_exe = Path(DIST_PATH) / NOMBRE_EXE.replace(".exe", "")
        print(f"✅ GENERACIÓN COMPLETADA CORRECTAMENTE")
        print("=" * 60)
        print(f"\n📂 Carpeta de salida:")
        print(f"   {carpeta_exe.absolute()}")
        print(f"\n📦 Ejecutable principal:")
        print(f"   {(carpeta_exe / NOMBRE_EXE).absolute()}")
        print(f"\n💡 IMPORTANTE:")
        print(f"   - Distribuye toda la carpeta '{NOMBRE_EXE.replace('.exe', '')}/'")
        print(f"   - No separar el .exe de la carpeta _internal/")
        print(f"   - Los recursos, temas y caché COM están en _internal/")
        print(f"   - Outlook debe estar instalado en el sistema destino")
    else:
        print("❌ ERROR EN LA GENERACIÓN")
        print("=" * 60)
        print("\n💡 Detalles del error:")
        print("─" * 60)
        if result.stderr:
            print(result.stderr)
        else:
            print("   No se capturó stderr, revisa los logs en build/")
        print("─" * 60)
    print("=" * 60)

# ==========================================================
# VERIFICAR SCRIPT PRINCIPAL
# ==========================================================
def verificar_main():
    """Verifica que exista el script principal"""
    ruta = Path.cwd() / MAIN_SCRIPT
    if not ruta.is_file():
        print(f"❌ ERROR: No se encontró '{MAIN_SCRIPT}' en el directorio actual.")
        print(f"   Asegúrate de ejecutar este script desde la raíz del proyecto.")
        sys.exit(1)
    else:
        print(f"✅ Archivo principal encontrado: {MAIN_SCRIPT}\n")

# ==========================================================
# VERIFICAR ESTRUCTURA DEL PROYECTO
# ==========================================================
def verificar_estructura():
    """Verifica que existan las carpetas y archivos necesarios"""
    print("🔍 Verificando estructura del proyecto:")
    print("=" * 60)
    
    base_dir = Path.cwd()
    
    # Carpetas críticas
    carpetas_requeridas = [
        "ui",
        "ui/tabs",
        "ui/widgets",
        "core",
        "utils",
        "workers",
        "config"
    ]
    
    # Archivos críticos
    archivos_requeridos = [
        "main.py",
        "config/app.ico",
        "config/config.json",
        "config/theme_dark.json",
        "config/theme_light.json",
        "ui/main_window.py",
        "ui/splash_screen.py",
        "core/email_extractor.py",
        "core/sign_classifier.py",
    ]
    
    todo_ok = True
    
    print("\n📁 Carpetas:")
    for carpeta in carpetas_requeridas:
        ruta = base_dir / carpeta
        if ruta.exists():
            print(f"   ✅ {carpeta}/")
        else:
            print(f"   ❌ {carpeta}/ NO ENCONTRADA")
            todo_ok = False
    
    print("\n📄 Archivos:")
    for archivo in archivos_requeridos:
        ruta = base_dir / archivo
        if ruta.exists():
            print(f"   ✅ {archivo}")
        else:
            print(f"   ⚠️  {archivo} no encontrado")
    
    if not todo_ok:
        print("\n❌ ERROR: Estructura del proyecto incompleta.")
        print("   Asegúrate de ejecutar este script desde la raíz del proyecto.")
        print("   Deben existir todas las carpetas: ui/, core/, config/, etc.")
        sys.exit(1)
    
    print("\n" + "=" * 60)


# ==========================================================
# EJECUCIÓN PRINCIPAL
# ==========================================================
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("   GENERADOR DE EJECUTABLE - MATRIXMAE")
    print("   Proyecto: OutlookExtractor")
    print("   Modo: Onedir (carpeta distribuible)")
    print("   Framework: PySide6 + Outlook COM")
    print("=" * 60 + "\n")
    
    try:
        verificar_main()
        verificar_estructura()
        validar_entorno_virtual()
        confirmar_ejecucion()
        generar_exe()
        
        print("\n" + "=" * 60)
        print("🎉 PROCESO COMPLETADO EXITOSAMENTE")
        print("=" * 60)
        print("\n💡 PRÓXIMOS PASOS:")
        print("   1. Prueba el ejecutable localmente")
        print("   2. Verifica conexión con Outlook")
        print("   3. Prueba cambiar de tema (Dark ↔ Light)")
        print("   4. Verifica extracción de adjuntos")
        print("   5. Prueba clasificación de documentos")
        print("   6. Verifica que los logs se generen correctamente")
        print("   7. Distribuye toda la carpeta 'OutlookExtractor/'\n")
        print("⚠️  IMPORTANTE: Outlook debe estar instalado en el sistema destino\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Proceso interrumpido por el usuario.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)