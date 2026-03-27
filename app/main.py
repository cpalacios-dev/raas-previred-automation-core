"""
Punto de entrada principal del sistema RaaS - Pago Remuneraciones.
Ejecuta este archivo para correr el robot de actualización de parámetros Previred.
"""
import sys
from pathlib import Path

# Agregar el directorio raíz al path para imports absolutos
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import logging
import asyncio
from app.config import get_settings
from app.core import Task
from app.robots import PreviredRobot


def configurar_logs():
    """Configura el sistema de logging."""
    config = get_settings()
    
    # Crear directorio de logs si no existe
    config.BASE_DIR.joinpath("logs").mkdir(parents=True, exist_ok=True)
    
    # Configuración de logging
    log_file = config.BASE_DIR / "logs" / "robot.log"
    
    logging.basicConfig(
        level=logging.INFO if not config.DEBUG_MODE else logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )


async def iniciar_proceso_parametros():
    """Función principal que ejecuta el robot."""
    
    # Configurar logging
    configurar_logs()
    logger = logging.getLogger("MAIN")
    
    logger.info("=" * 60)
    logger.info("Sistema RaaS - Pago Remuneraciones")
    logger.info("=" * 60)
    
    # Cargar configuración
    config = get_settings()
    logger.info(f"Entorno: {config.DEBUG_MODE and 'DEBUG' or 'PRODUCTION'}")
    logger.info(f"Proceso: {config.PROCESS_NAME}")
    
    # Crear tarea
    tarea = Task(
        name="Actualización Parámetros Previred",
        robot_name="pagoremuneraciones",
        parameters={}
    )
    
    logger.info(f"Tarea creada: {tarea.name} [ID: {tarea.id}]")
    
    # Instanciar y ejecutar robot
    try:
        robot = PreviredRobot(config, logger)
        resultado = await robot.run(tarea)
        
        logger.info("=" * 60)
        if resultado.success:
            logger.info("Ejecución exitosa")
            logger.info(f"Mensaje: {resultado.message}")
            if resultado.data:
                for key, value in resultado.data.items():
                    logger.info(f"  - {key}: {value}")
        else:
            logger.error("Ejecución fallida")
            logger.error(f"Error: {resultado.error}")
        logger.info("=" * 60)
                
    except Exception as e:
        logger.error(f"Error crítico: {e}", exc_info=True)
        sys.exit(1)


def main():
    """Wrapper para compatibilidad."""
    asyncio.run(iniciar_proceso_parametros())


if __name__ == "__main__":
    main()
