# Robots

Este directorio contiene los robots del sistema RaaS.

## Estructura

Cada robot debe estar en su propia carpeta con la siguiente estructura:

```
robots/
└── mi_robot/
    ├── __init__.py          # Exporta la clase del robot
    ├── robot.py             # Implementación del robot
    └── config.json          # Configuración del robot (opcional)
```

## Crear un Nuevo Robot

1. **Crear el directorio del robot:**
   ```
   robots/mi_robot/
   ```

2. **Crear `robot.py`:**
   ```python
   from core import BaseRobot, Task, TaskResult
   
   class MiRobot(BaseRobot):
       def execute(self, task: Task) -> TaskResult:
           # Tu lógica aquí
           return TaskResult(success=True, message="OK")
   ```

3. **Crear `__init__.py`:**
   ```python
   from .robot import MiRobot
   __all__ = ["MiRobot"]
   ```

4. **Actualizar `main.py`** para usar tu nuevo robot.

## Robots Disponibles

### PagoRemuneracionesRobot
- **Descripción:** Extrae parámetros de Previred y los sube a GCP
- **Ubicación:** `robots/pagoremuneraciones_robot/`
- **Autor:** TransformacionIT
