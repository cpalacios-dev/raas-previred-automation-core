# Estructura del Proyecto - RaaS Pago Remuneraciones v2.0

## 📁 Estructura de Directorios

```
raas_004_pagoremuneraciones-ms_back/
│
├── 📄 run_local.ps1              # Script para ejecutar en desarrollo
├── 📄 test_local_headless.ps1    # Script para pruebas headless
├── 📄 requirements.txt           # Dependencias del proyecto
├── 📄 Dockerfile                 # Configuración Docker
├── 📄 README.md                  # Documentación principal
├── 📄 ESTRUCTURA.md              # Este archivo
│
├── 📁 app/                       # ⭐ APLICACIÓN PRINCIPAL
│   ├── __init__.py
│   ├── 📄 main.py                # Punto de entrada principal
│   ├── 📄 app.py                 # API REST simplificada
│   │
│   ├── 📁 config/                # ⚙️ Configuración global
│   │   ├── __init__.py
│   │   └── settings.py           # Variables de entorno y configuración
│   │
│   ├── 📁 core/                  # 🎯 Componentes básicos del sistema
│   │   ├── __init__.py
│   │   ├── task.py               # Task, TaskResult, TaskStatus
│   │   └── base_robot.py         # Clase base para todos los robots
│   │
│   ├── 📁 models/                # 📊 Modelos de datos
│   │   ├── __init__.py
│   │   ├── entities.py           # Entidades del dominio (ParametroPrevired, etc)
│   │   └── interfaces.py         # Interfaces de servicios (contratos)
│   │
│   ├── 📁 helpers/               # 🔧 Herramientas útiles
│   │   ├── __init__.py
│   │   ├── selenium_helper.py    # Automatización web con Playwright
│   │   ├── data_processing.py    # Procesamiento de datos y tablas
│   │   └── resilience.py         # Decoradores de reintento
│   │
│   ├── 📁 robots/                # 🤖 Robots del sistema
│   │   ├── __init__.py
│   │   ├── README.md             # Guía para crear robots
│   │   └── pagoremuneraciones_robot/ # Robot de parámetros Previred
│   │       ├── __init__.py
│   │       ├── config.json       # Configuración del robot
│   │       └── robot.py          # Implementación
│   │
│   ├── 📁 services/              # 🌐 Servicios externos
│   │   ├── __init__.py
│   │   ├── gcp_service.py        # Google Cloud Storage
│   │   └── mail_service.py       # Envío de correos (SendGrid)
│   │
│   ├── 📁 data/                  # 💾 Archivos de trabajo
│   │   ├── input/                # Archivos de entrada
│   │   │   └── .gitkeep
│   │   └── output/               # Resultados generados (CSV)
│   │       └── .gitkeep
│   │
│   ├── 📁 logs/                  # 📊 Logs del sistema
│   │   └── .gitkeep
│   │
│   ├── 📁 templates/             # 📧 Plantillas
│   │   └── emails/               # Plantillas HTML para correos
│   │       ├── exito.html
│   │       └── error_generico.html
│   │
│   └── 📁 tests/                 # ✅ Tests
│       ├── __init__.py
│       ├── test_basics.py
│       ├── fixtures/
│       ├── integration/
│       └── unit/
│
├── 📁 overlays/                  # 🔐 Configuración por entorno
│   ├── dev/
│   │   ├── .env.yaml             # Configuración base desarrollo
│   │   └── .env.local.yaml       # Credenciales locales (no versionado)
│   ├── qa/
│   │   └── .env.yaml             # Configuración QA
│   └── prod/
│       └── .env.yaml             # Configuración producción
│
└── 📁 .github/                   # CI/CD
    └── workflows/
        └── pipeline.yaml
```

## 🎯 Archivos Clave

| Archivo | Descripción | Cuándo usarlo |
|---------|-------------|---------------|
| `app/main.py` | Ejecuta robots | Ejecución directa |
| `app/api.py` | API REST con callbacks | Integración legacy |
| `app/app.py` | API REST simplificada | Ejecución de servicios |
| `app/core/task.py` | Define Task y TaskResult | Solo lectura |
| `app/core/base_robot.py` | Clase base BaseRobot | Heredar de esta |
| `app/models/` | Entidades e interfaces | Definir contratos |
| `app/helpers/*.py` | Herramientas listas | Importar en robots |
| `app/robots/*/robot.py` | Tu código de robot | Crear nuevos aquí |
| `run_local.ps1` | Script de ejecución | Desarrollo local |

## 🚀 Flujo de Trabajo

```
1. Leer README.md (10 min)
   ↓
2. Configurar overlays/dev/.env.yaml
   ↓
3. Ejecutar ./run_local.ps1
   ↓
4. Ver logs en app/logs/
   ↓
5. Ver resultados en app/data/output/
```

## 📊 Comparación con Versión Anterior

### v1.0 (Estructura Plana)
```
raas_004/
├── Main.py
├── settings.py
├── browser_manager.py
├── process_actualizacion_parametros.py
├── config/
├── core/
└── ...
```

### v2.0 (Estructura con app/)
```
raas_004/
├── run_local.ps1
├── app/
│   ├── main.py
│   ├── api.py
│   ├── app.py
│   ├── config/
│   ├── core/
│   ├── models/      ← NUEVO
│   ├── helpers/
│   ├── robots/
│   └── ...
└── overlays/
```

## 🆕 Novedades v2.0

1. **Carpeta `app/`**: Todo el código de la aplicación contenido
2. **Models**: Entidades e interfaces para arquitectura limpia
3. **app.py**: API simplificada sin callbacks
4. **Scripts**: `run_local.ps1` y `test_local_headless.ps1`
5. **Imports con prefijo**: Todos usan `from app.xxx import ...`

## 🔄 Arquitectura RaaS v2.0

```
┌─────────────────────────────────────────┐
│         app/main.py (Entry Point)       │
└───────────────┬─────────────────────────┘
                │
                ↓
┌───────────────────────────────────────────┐
│         Task System (app/core/task.py)    │
│  - Task                                   │
│  - TaskResult                             │
│  - TaskStatus                             │
└───────────────┬───────────────────────────┘
                │
                ↓
┌─────────────────────────────────────────────────┐
│   Robot (app/robots/.../robot.py)               │
│   Hereda de: BaseRobot                          │
│   Ciclo:     setup → execute → teardown         │
└──────┬──────────────────┬────────────────┬──────┘
       │                  │                │
       ↓                  ↓                ↓
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Helpers    │  │   Services   │  │    Models    │
│  (app/...)   │  │  (app/...)   │  │  (app/...)   │
└──────────────┘  └──────────────┘  └──────────────┘
```

## 📚 Documentación Adicional

- [README.md](README.md) - Visión general y guía de uso
- [MIGRACION.md](MIGRACION.md) - Guía de migración desde v1.0
- [app/robots/README.md](app/robots/README.md) - Cómo crear robots

## ⚠️ Notas Importantes

1. Todos los imports deben usar el prefijo `app.`: `from app.config import ...`
2. Las rutas ahora son relativas a `app/`: `app/data/output/`
3. Los logs se guardan en `app/logs/`
4. La configuración se carga desde `overlays/{ENV}/.env.yaml`
5. Ejecutar siempre desde la raíz del proyecto

## 🐛 Solución de Problemas

### Error: "No module named 'app'"
- Asegúrate de ejecutar desde la raíz del proyecto
- Verifica que `sys.path` incluye el directorio raíz

### Error: "No module named 'app.config'"
- Verifica que existe `app/config/__init__.py`
- Verifica las importaciones en `app/config/__init__.py`

### Error: overlays no encontrado
- Asegúrate de tener `overlays/dev/.env.yaml`
- Verifica la variable de entorno `ENV`
