# RPA - Actualización de Parámetros Previred

<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white"/> | <img src="https://img.shields.io/badge/Playwright-2EAD33?style=for-the-badge&logo=playwright&logoColor=white" /> | <img src="https://img.shields.io/badge/Google_Cloud-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white" /> | <img src="https://img.shields.io/badge/SendGrid-Interactivo-blue?style=for-the-badge&logo=sendgrid&logoColor=white" />

## Comenzando 🚀
Este repositorio contiene la automatización encargada de la extracción, procesamiento y centralización de indicadores previsionales desde el portal **Previred**.

El proceso automatiza la obtención de valores clave como **UF, UTM, Tasas AFP y Rentas Topes** para consolidarlos en un archivo CSV. Una vez procesados, los datos se respaldan en un Bucket de **Google Cloud Storage** y se notifican los resultados mediante la API de **SendGrid**.

## Estructura del Proyecto 📂
🎉 **El proyecto sigue la arquitectura RaaS v2.0** con toda la aplicación contenida en la carpeta `app/`:

## Estructura del Proyecto 📂
🎉 **El proyecto sigue la arquitectura RaaS v2.0** con toda la aplicación contenida en la carpeta `app/`:

```text
raas-previred-automation-core/
├── 📄 .gitignore                 # Exclusión de archivos sensibles
├── 📄 requirements.txt           # Dependencias del proyecto
├── 📄 Dockerfile                 # Configuración para Cloud Run / Contenedores
│
├── 📁 app/                       # ⭐ Núcleo de la Aplicación
│   ├── 📄 main.py                # Ejecución directa (CLI / Desarrollo)
│   ├── 📄 app.py                 # API REST de producción
│   │
│   ├── 📁 config/                # Gestión de variables por entorno
│   ├── 📁 core/                  # Clases base y ciclo de vida (BaseRobot)
│   ├── 📁 helpers/               # Scraping, Procesamiento y Resiliencia
│   ├── 📁 robots/                # Implementación del Robot Previred
│   ├── 📁 services/              # Clientes de GCP Storage y SendGrid
│   └── 📁 data/                  # Directorios de entrada/salida (CSV)
│
└── 📁 overlays/                  # 🔐 Configuración YAML por entorno (Dev/QA/Prod)

```

Ver [ESTRUCTURA.md](ESTRUCTURA.md) para más detalles.

## Herramientas utilizadas 📋
- **Python 3.12+**: Lenguaje base del proyecto.
- **Playwright**: Utilizado para la navegación y control del navegador.
- **BeautifulSoup4 (lxml)**: Para el parseo y extracción de tablas HTML.
- **Pandas**: Para la manipulación de datos y generación del DataFrame.
- **Google Cloud Storage (GCS)**: Para el almacenamiento persistente en la nube.
- **SendGrid API**: Servicio para el envío de notificaciones por correo electrónico.
- **Pydantic Settings**: Para gestión de configuración y variables de entorno.
- **Flask**: Para la API REST.

## Instalación y Ejecución 💻

### Instalación
```bash
# 1. Crear entorno virtual
python -m venv venv

# 2. Activar entorno virtual
# En Windows:
.\venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Instalar navegadores Playwright
playwright install chromium

# 5. Configurar variables de entorno
# Editar overlays/{env}/.env.yaml según el entorno
```

### Ejecución Local

#### Modo Directo (Recomendado para desarrollo)
```powershell
.\run_local.ps1
```

#### Modo Headless (Simula Cloud Run)
```powershell
.\test_local_headless.ps1
```

#### Ejecución Manual
```bash
# Configurar entorno
$env:ENV = "dev"

# Ejecutar directamente
python app/main.py
```

### Ejecución de API

#### API Simplificada (app.py)
```bash
python app/app.py
```

## Arquitectura RaaS v2.0 🏗️

### Componentes Principales

1. **Task & TaskResult**: Sistema de tareas con estados

2. **BaseRobot**: Clase base con ciclo de vida (setup → execute → teardown)

3. **Models**: Entidades e interfaces para una arquitectura limpia

4. **Helpers**: Servicios reutilizables y helpers de negocio

5. **Services**: Integraciones con servicios externos

### Flujo de Ejecución

```
1. main.py crea una Task
   ↓
2. Instancia PagoRemuneracionesRobot
   ↓
3. Robot ejecuta:
   - setup() → Inicializa servicios
   - execute() → Lógica principal
   - teardown() → Limpia recursos
   ↓
4. Retorna TaskResult
```

## Configuración por Entorno 🔧

El proyecto usa archivos YAML en `overlays/` para configuración por entorno:

- **overlays/dev/.env.yaml**: Configuración base de desarrollo
- **overlays/dev/.env.local.yaml**: Credenciales locales (no versionado)
- **overlays/qa/.env.yaml**: Configuración de QA
- **overlays/prod/.env.yaml**: Configuración de producción


## Crear Nuevos Robots 🤖
Ver [app/robots/README.md](app/robots/README.md) para una guía completa sobre cómo crear nuevos robots.

## Testing ✅

```bash
# Ejecutar tests (cuando estén implementados)
pytest app/tests/
```

## Docker 🐳

```bash
# Construir imagen
docker build -t raas-pago-remuneraciones .

# Ejecutar contenedor
docker run -p 8080:8080 raas-pago-remuneraciones
```

## Extras 💡
- **Resiliencia**: Implementa decoradores de reintento (`@reintentar_accion`) para manejar fallos temporales
- **Logging**: Sistema de logging mejorado con archivos rotables en `app/logs/`
- **Modularidad**: Arquitectura limpia con separación de responsabilidades
- **Escalabilidad**: Preparado para múltiples robots y procesos

---
**Desarrollado por:** TransformacionIT  
**Arquitectura:** RaaS v2.0 (Robots as a Service)  
**Versión:** 2.0.0