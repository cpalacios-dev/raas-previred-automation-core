"""
Clase base para todos los robots.
Hereda de esta clase para crear nuevos robots.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any
import logging

from app.core.task import Task, TaskResult, TaskStatus


class BaseRobot(ABC):
    """
    Clase base que todos los robots deben heredar.
    
    Ejemplo de uso:
        class MiRobot(BaseRobot):
            def execute(self, task: Task) -> TaskResult:
                # Tu lógica aquí
                return TaskResult(success=True, message="OK")
    """
    
    def __init__(self, config, logger: logging.Logger):
        """
        Inicializa el robot base.
        
        Args:
            config: Configuración del robot
            logger: Logger para el robot
        """
        self.config = config
        self.logger = logger
    
    @abstractmethod
    async def execute(self, task: Task) -> TaskResult:
        """
        Implementa la lógica principal de tu robot.
        
        Args:
            task: Tarea con parámetros a ejecutar
            
        Returns:
            TaskResult con el resultado
        """
        pass
    
    def setup(self) -> None:
        """
        Opcional: Inicializa recursos antes de ejecutar.
        Ejemplo: Abrir navegador, conectar a BD, etc.
        """
        pass
    
    async def teardown(self) -> None:
        """
        Opcional: Limpia recursos después de ejecutar.
        Ejemplo: Cerrar navegador, cerrar conexiones, etc.
        """
        pass
    
    async def run(self, task: Task) -> TaskResult:
        """
        Ejecuta el robot completo (setup -> execute -> teardown).
        No necesitas sobrescribir este método.
        """
        try:
            self.logger.info(f"Iniciando robot: {self.__class__.__name__}")
            self.setup()
            
            task.status = TaskStatus.RUNNING
            result = await self.execute(task)
            
            task.mark_completed(result)
            self.logger.info(f"Robot finalizado: {'Éxito' if result.success else 'Fallo'}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error en robot: {str(e)}", exc_info=True)
            result = TaskResult(
                success=False,
                message="Error inesperado",
                error=str(e)
            )
            task.mark_completed(result)
            return result
            
        finally:
            try:
                await self.teardown()
            except Exception as e:
                self.logger.warning(f"Error en teardown: {str(e)}")
