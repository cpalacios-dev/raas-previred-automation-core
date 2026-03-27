"""Módulo core - Componentes básicos del sistema."""
from .task import Task, TaskResult, TaskStatus
from .base_robot import BaseRobot

__all__ = ["Task", "TaskResult", "TaskStatus", "BaseRobot"]
