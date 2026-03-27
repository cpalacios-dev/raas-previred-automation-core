"""
Entidades básicas del sistema RaaS.
Define Task y TaskResult de forma simple.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from uuid import UUID, uuid4


class TaskStatus(Enum):
    """Estados de una tarea."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class TaskResult:
    """Resultado de ejecutar un robot."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class Task:
    """
    Representa una tarea que ejecutará un robot.
    
    Ejemplo:
        task = Task(
            name="Procesar parámetros Previred",
            robot_name="pagoremuneraciones",
            parameters={}
        )
    """
    name: str
    robot_name: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    id: UUID = field(default_factory=uuid4)
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    finished_at: Optional[datetime] = None
    result: Optional[TaskResult] = None
    
    def mark_completed(self, result: TaskResult) -> None:
        """Marca la tarea como completada."""
        self.status = TaskStatus.COMPLETED if result.success else TaskStatus.FAILED
        self.finished_at = datetime.now()
        self.result = result
