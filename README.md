# 📧 OutlookExtractor - Gestor Automatizado de Correos Outlook

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/PySide6-6.0+-green.svg)](https://pypi.org/project/PySide6/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)
[![Version](https://img.shields.io/badge/Version-3.0.0-orange.svg)](https://github.com/Merlin2098/Outlook_AttachExtractor_Rework)

## 📋 Descripción

**OutlookExtractor** (Matrix Mail Attach Extractor) es una aplicación de escritorio profesional desarrollada en Python con PySide6 que automatiza la gestión de correos electrónicos de Microsoft Outlook. Diseñada para entornos empresariales, permite extraer adjuntos de manera masiva y clasificar documentos según su estado de firma digital, procesando eficientemente miles de correos durante operaciones extendidas.

### 🎯 Características Principales

- **📥 Extracción Masiva de Adjuntos**

  - Sistema de auditoría basado en Entry IDs para máxima precisión
  - Filtrado avanzado por frases clave con tres modos: coincidencia total, palabras parciales, sin filtro
  - Búsqueda limitada al asunto del correo para optimizar rendimiento
  - Detección automática del rango de fechas disponible en la bandeja
  - Sistema anti-duplicados inteligente
  - Generación de reportes detallados en Excel con metadata completa
  - Mapeo completo de correos mediante Parquet/Polars para debugging avanzado
- **🔍 Clasificación de Documentos**

  - Organización automática según estado de firma digital
  - Detección de patrones: `firmado`, `signed`, `sin_firmar`, `not_signed`
  - Estadísticas en tiempo real del proceso
  - Manejo seguro de archivos duplicados con subcarpetas opcionales
- **🎨 Interfaz Moderna y Modular**

  - Arquitectura basada en widgets reutilizables
  - Sistema de temas claro/oscuro con persistencia de preferencias
  - Configuración de temas mediante JSON independientes
  - Progress bar detallado por fase de operación
  - Splash screen con lazy loading para inicio rápido
  - Logs en tiempo real con códigos de color
  - Notificaciones visuales y sonoras al completar tareas
  - Selector inteligente de carpetas de Outlook
- **⚡ Optimizaciones Empresariales**

  - Power Manager: previene suspensión del equipo durante procesos largos
  - Sistema de logging dual: sesión actual + histórico de errores
  - Auto-limpieza de logs (máximo 50 de cada tipo, elimina > 30 días)
  - Procesamiento eficiente con Entry IDs para evitar omisiones
  - Auditoría completa de correos procesados vs. omitidos

## 🆕 Novedades en v3.0.0

### Migración a PySide6

- Migración completa desde PyQt5 a PySide6
- Modularización total de la UI mediante sistema de widgets
- Mejor rendimiento y compatibilidad futura

### Sistema de Auditoría Avanzado

- Mapeo completo de correos mediante Entry IDs únicos
- Generación de archivos Parquet para análisis y debugging
- Reportes Excel detallados mostrando correos procesados y omitidos con causas

### Mejoras de UX

- Progress bar tool con indicadores por fase
- Búsqueda por frases customizada con tres modos de coincidencia
- Sistema de temas JSON independientes para fácil personalización
- Widgets especializados para mejor interacción visual

### Gestión de Sistema

- Power Manager: evita suspensión automática durante procesos
- Sistema de logging dual con timestamps
- Auto-limpieza inteligente de logs históricos

## 🚀 Instalación

### Requisitos Previos

- **Sistema Operativo:** Windows 10/11
- **Python:** 3.13 o superior
- **Microsoft Outlook:** Classic version (instalado y configurado)
  - ⚠️ **Importante:** No usar "New Outlook", solo Outlook Classic
  - Los correos deben estar en caché local según configuración de Outlook
- **Permisos:** Administrador (recomendado)

### Instalación desde Código Fuente

1. **Clonar el repositorio:**

```bash
git clone https://github.com/Merlin2098/Outlook_AttachExtractor_Rework.git
cd Outlook_AttachExtractor_Rework
```

2. **Crear entorno virtual:**

```bash
python -m venv venv
venv\Scripts\activate
```

3. **Instalar dependencias:**

```bash
pip install -r requirements.txt
```

4. **Ejecutar la aplicación:**

```bash
python main.py
```

### Instalación desde Ejecutable

1. Descargar el paquete desde [Releases](https://github.com/Merlin2098/Outlook_AttachExtractor_Rework/releases)
2. Extraer la carpeta completa `OutlookExtractor/`
3. Ejecutar `OutlookExtractor.exe`
4. **Nota:** Distribuir la carpeta completa, no solo el ejecutable

## 🛠️ Desarrollo

### Estructura del Proyecto

```
OutlookExtractor/
├── .gitignore
├── .pre-commit-config.yaml
├── config/                      # Configuración y recursos
│   ├── __init__.py
│   ├── app.ico                  # Icono de la aplicación
│   ├── config.json              # Configuración persistente (tema, ventana)
│   ├── config_manager.py        # Gestor singleton de configuración
│   ├── theme_dark.json          # Paleta de colores tema oscuro
│   └── theme_light.json         # Paleta de colores tema claro
│
├── core/                        # Lógica de negocio
│   ├── __init__.py
│   ├── backend_base.py          # Clase base abstracta para backends
│   ├── email_extractor.py       # Lógica de extracción de adjuntos
│   └── sign_classifier.py       # Lógica de clasificación por firma
│
├── ui/                          # Componentes de interfaz
│   ├── __init__.py
│   ├── main_window.py           # Ventana principal de la aplicación
│   ├── splash_screen.py         # Pantalla de carga con lazy loading
│   ├── theme_manager.py         # Gestor de temas con widgets
│   ├── tabs/                    # Pestañas de funcionalidad
│   │   ├── __init__.py
│   │   ├── base_tab.py          # Clase base para pestañas
│   │   ├── tab_clasificador.py  # Pestaña de clasificación
│   │   └── tab_extractor.py     # Pestaña de extracción
│   └── widgets/                 # Widgets reutilizables
│       ├── __init__.py
│       ├── author_info_widget.py      # Info del autor
│       ├── base_widget.py             # Widget base
│       ├── date_range_widget.py       # Selector de rango de fechas
│       ├── folder_selector_widget.py  # Selector de carpetas del sistema
│       ├── outlook_folder_selector.py # Selector de carpetas de Outlook
│       ├── phrase_search_widget.py    # Búsqueda por frases
│       ├── progress_widget.py         # Barra de progreso detallada
│       └── theme_toggle_widget.py     # Alternador de tema
│
├── workers/                     # Capa de threading
│   ├── __init__.py
│   ├── base_worker.py           # Worker base con señales Qt
│   ├── classifier_worker.py     # Worker para clasificación
│   └── extractor_worker.py      # Worker para extracción
│
├── utils/                       # Utilidades del sistema
│   ├── __init__.py
│   ├── audit_mails.py           # Auditoría de correos con Parquet
│   ├── date_handler.py          # Manejo de fechas y rangos
│   ├── logger.py                # Sistema de logging dual (MatrixLogger)
│   ├── notification_utils.py    # Notificaciones del sistema
│   └── power_manager.py         # Prevención de suspensión
│
├── generar_onedir.py            # Script para generar ejecutable
├── runtime_hook_com.py          # Hook para PyInstaller + COM
├── main.py                      # Punto de entrada de la aplicación
├── requirements.txt             # Dependencias del proyecto
├── LICENSE                      # Licencia MIT
└── README.md                    # Este archivo
```

### Arquitectura en 3 Capas

El proyecto implementa una arquitectura limpia y modular:

```
┌─────────────────────────────────────────────┐
│         Core (Lógica de Negocio)            │
│  • backend_base.py - Clase abstracta base   │
│  • email_extractor.py - Extracción          │
│  • sign_classifier.py - Clasificación       │
└─────────────────────────────────────────────┘
                    ▲
                    │
┌─────────────────────────────────────────────┐
│      Workers (Capa de Threading/Señales)    │
│  • base_worker.py - Worker base Qt          │
│  • extractor_worker.py - Threading extrac.  │
│  • classifier_worker.py - Threading clasif. │
└─────────────────────────────────────────────┘
                    ▲
                    │
┌─────────────────────────────────────────────┐
│          UI (Interfaz de Usuario)           │
│  • main_window.py - Ventana principal       │
│  • tabs/ - Pestañas funcionales             │
│  • widgets/ - Componentes reutilizables     │
│  • theme_manager.py - Gestión de temas      │
└─────────────────────────────────────────────┘
```

**Principios de Diseño:**

- **Separación de responsabilidades:** Cada capa tiene un rol específico
- **Modularidad:** Widgets y componentes reutilizables
- **Comunicación por señales:** Qt Signals/Slots para threading seguro
- **Configuración centralizada:** JSON para temas y preferencias

### Sistema de Auditoría con Entry IDs

Una de las mejoras clave de v3.0.0 es el sistema de auditoría:

1. **Mapeo Inicial:** Se mapean todos los correos de la bandeja mediante Entry IDs únicos
2. **Almacenamiento:** Los datos se guardan en formato Parquet usando Polars
3. **Filtrado Preciso:** Se aplican filtros sobre el Parquet para identificar correos elegibles
4. **Descarga Selectiva:** Solo se procesan los Entry IDs que cumplen condiciones
5. **Reporte Detallado:** Excel muestra correos procesados vs. omitidos con causas

**Ventajas:**

- Elimina omisiones de correos durante procesamiento masivo
- Permite debugging avanzado con datos históricos
- Mejora precisión en operaciones de miles de correos

## 🔧 Configuración

### config.json

```json
{
  "tema": "claro",
  "ui": {
    "window_size": [1200, 700]
  }
}
```

**Parámetros:**

- `tema`: Último tema seleccionado (`"claro"` o `"oscuro"`)
- `window_size`: Dimensiones de la ventana `[ancho, alto]`

### theme_light.json / theme_dark.json

Archivos JSON que definen la paleta de colores para cada tema. Pueden editarse para personalizar la apariencia:

```json
{
  "background": "#FFFFFF",
  "foreground": "#000000",
  "accent": "#0078D4",
  "border": "#CCCCCC",
  ...
}
```

### Sistema de Logging

**MatrixLogger** implementa un sistema dual:

- **Logs de Sesión:** `session_YYYYMMDD_HHMMSS.log`
- **Logs de Errores:** `errors_YYYYMMDD_HHMMSS.log`

**Configuración Automática:**

- Retención: Máximo 50 logs de cada tipo
- Limpieza: Elimina logs con más de 30 días
- Ubicación: Carpeta `logs/` en el directorio de la aplicación

## 📖 Uso

### Extracción de Adjuntos

1. **Abrir pestaña "Descarga de Adjuntos"**
2. **Seleccionar carpeta de Outlook:**

   - Clic en botón **"📧 Explorar Carpetas de Outlook"**
   - Navegar por la estructura de carpetas
   - Seleccionar la bandeja deseada
3. **Configurar filtros:**

   - **Frases de búsqueda:** Separadas por coma (ej: `factura, recibo, contrato`)
   - **Modo de coincidencia:**
     - Coincidencia total: El asunto debe contener todas las frases
     - Algunas palabras: El asunto debe contener al menos una frase
     - Sin filtro: Procesar todos los correos del rango
   - **Rango de fechas:** Inicio y fin (auto-detecta rango disponible)
   - **Carpeta destino:** Dónde guardar los adjuntos extraídos
4. **Iniciar proceso:**

   - Clic en **"▶️ Iniciar Descarga"**
   - Monitorear progreso en la barra detallada
   - Revisar logs en tiempo real
5. **Revisar resultados:**

   - Adjuntos guardados en carpeta destino
   - Reporte Excel con metadata completa
   - Archivo Parquet para auditoría técnica

### Clasificación de Documentos

1. **Abrir pestaña "Clasificar Documentos"**
2. **Seleccionar carpetas:**

   - **Carpeta origen:** Documentos a clasificar
   - **Carpeta destino:** Donde se organizarán
3. **Iniciar clasificación:**

   - Clic en **"▶️ Iniciar Clasificación"**
   - Observar estadísticas en tiempo real:
     - Total de archivos procesados
     - Documentos firmados vs. sin firmar
     - Archivos duplicados detectados
4. **Revisar resultados:**

   - Carpeta destino contendrá subcarpetas:
     - `firmados/` o `signed/`
     - `sin_firmar/` o `not_signed/`
   - Log detallado de todas las operaciones

### Modos de Búsqueda por Frases

| Modo                         | Descripción                               | Ejemplo                                                                        |
| ---------------------------- | ------------------------------------------ | ------------------------------------------------------------------------------ |
| **Coincidencia Total** | El asunto debe contener TODAS las frases   | Busca:`factura, enero` → Encuentra: "Factura del mes de enero 2024"         |
| **Algunas Palabras**   | El asunto debe contener AL MENOS UNA frase | Busca:`factura, recibo` → Encuentra: "Envío de factura" o "Recibo adjunto" |
| **Sin Filtro**         | Procesa TODOS los correos del rango        | Ignora frases, solo aplica filtro de fechas                                    |

## 🔄 Migración desde v2.0.0 (PyQt5)

Si vienes de la versión anterior, estos son los cambios principales:

### Cambios de Interfaz

- ✅ Misma funcionalidad core, interfaz modernizada
- ✅ Sistema de widgets modulares para mejor mantenimiento
- ✅ Temas JSON independientes (antes hardcoded)
- ✅ Progress bar mejorada con indicadores por fase

### Cambios Técnicos

- ✅ PySide6 en lugar de PyQt5
- ✅ Entry IDs para identificación precisa de correos
- ✅ Sistema de auditoría con Parquet/Polars
- ✅ Power Manager para procesos largos
- ✅ Logging dual con auto-limpieza

### Compatibilidad

- ⚠️ Requiere Python 3.13+ (antes 3.8+)
- ⚠️ Solo Outlook Classic (New Outlook no soportado)
- ✅ Config.json compatible, migración automática de preferencias

## 🏗️ Generar Ejecutable

Para crear una distribución ejecutable con PyInstaller:

1. **Activar entorno virtual:**

```bash
venv\Scripts\activate
```

2. **Ejecutar script de generación:**

```bash
python generar_onedir.py
```

3. **Distribución:**
   - El ejecutable se genera en `dist/OutlookExtractor/`
   - **Importante:** Distribuir la carpeta completa, no solo el `.exe`
   - `config.json` puede editarse post-distribución

### Consideraciones Especiales PySide6 + COM

El archivo `runtime_hook_com.py` es esencial para:

- Inicialización correcta de objetos COM en el bundle
- Compatibilidad con interfaces de Outlook
- Prevención de errores de threading en distribución

**Nota:** Este hook se genera automáticamente al ejecutar `generar_onedir.py` y puede eliminarse en desarrollo.

## 🛡️ Solución de Problemas

### ❌ "No se puede conectar a Outlook"

**Causas comunes:**

- Outlook no instalado o no configurado
- Usando "New Outlook" en lugar de "Outlook Classic"
- Permisos insuficientes

**Soluciones:**

1. Verificar que Outlook Classic esté instalado
2. Ejecutar la aplicación como administrador
3. Asegurar que Outlook no esté en modo seguro
4. Configurar al menos una cuenta en Outlook

### ❌ "No se encuentran correos en el rango especificado"

**Diagnóstico:**

- Revisar el rango real disponible mostrado en logs iniciales
- Verificar configuración de caché de Outlook (correos deben estar en local)

**Soluciones:**

1. Ajustar fechas según rango disponible en bandeja
2. Verificar que las frases de búsqueda sean correctas
3. Probar modo "Sin Filtro" para descartar problema de frases
4. Revisar archivo Parquet de auditoría para debugging

### ❌ "Proceso se detiene después de 8000+ correos"

**Causa:** Acumulación de objetos COM sin liberar

**Solución:** Esta versión implementa gestión automática de memoria COM. Si persiste:

1. Revisar logs de errores para detalles específicos
2. Procesar en lotes más pequeños (rangos de fechas menores)
3. Contactar soporte con archivo de log

### ⚠️ "El equipo se suspendió durante el proceso"

**Solución:** El Power Manager debe prevenir esto automáticamente. Si ocurre:

1. Verificar que la aplicación tenga permisos de administrador
2. Revisar configuración de energía de Windows
3. Considerar deshabilitar suspensión manualmente para procesos críticos

### 🐛 Limitaciones Conocidas

- **Outlook Classic Only:** No compatible con "New Outlook"
- **Caché Local:** Solo procesa correos disponibles en caché de Outlook
- **Windows Only:** Diseñado específicamente para Windows 10/11
- **COM Threading:** Procesos muy extensos (>20,000 correos) pueden requerir monitoreo

## 🤝 Contribuir

Las contribuciones son bienvenidas. Para contribuir:

1. Fork el proyecto
2. Crear una rama para tu feature:
   ```bash
   git checkout -b feature/NuevaFuncionalidad
   ```
3. Commit con mensajes descriptivos:
   ```bash
   git commit -m 'feat: Agregar funcionalidad X'
   ```
4. Push a tu rama:
   ```bash
   git push origin feature/NuevaFuncionalidad
   ```
5. Abrir un Pull Request con descripción detallada

### Guías de Estilo

- **Código Python:** Seguir PEP 8
- **Docstrings:** Documentar todas las funciones públicas
- **Commits:** Usar [Conventional Commits](https://www.conventionalcommits.org/)
- **Módulos nuevos:** Actualizar treemap.md y README.md
- **Widgets:** Heredar de `base_widget.py` para consistencia

### Áreas de Contribución

- 🧪 Implementar suite de tests (actualmente removida)
- 📊 Mejorar reportes Excel con gráficos
- 🌐 Internacionalización (i18n)
- 🚀 Optimizaciones de rendimiento
- 📱 Interfaz responsive para diferentes resoluciones
- 🔌 Soporte para otros clientes de correo (Thunder bird, etc.)

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## 👨‍💻 Autor

**Richi** - [GitHub](https://github.com/Merlin2098)

**📌 Última actualización:** Enero 2025 | **🏷️ Versión:** 3.0.0

**⭐ Si este proyecto te resulta útil, considera darle una estrella en GitHub!**
