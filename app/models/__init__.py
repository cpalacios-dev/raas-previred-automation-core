"""Módulo de modelos de datos."""
from .entities import ParametroPrevired, ResultadoProceso
from .interfaces import (
    IWebScrapingService,
    IStorageService,
    INotificationService,
    IDataProcessor
)

__all__ = [
    "ParametroPrevired",
    "ResultadoProceso",
    "IWebScrapingService",
    "IStorageService",
    "INotificationService",
    "IDataProcessor"
]
