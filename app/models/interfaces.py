"""
Interfaces (contratos) para los servicios del sistema.
Define los métodos que deben implementar los servicios.
"""
from abc import ABC, abstractmethod
from typing import Optional, List


class IWebScrapingService(ABC):
    """Interfaz para servicios de web scraping."""
    
    @abstractmethod
    async def navegar_y_extraer_tablas(self) -> list:
        """Navega al sitio web y extrae las tablas HTML."""
        pass
    
    @abstractmethod
    async def cerrar(self) -> None:
        """Cierra el navegador y libera recursos."""
        pass


class IStorageService(ABC):
    """Interfaz para servicios de almacenamiento en la nube."""
    
    @abstractmethod
    def subir_archivo(self, ruta_local_archivo: str, ruta_destino: str) -> str:
        """
        Sube un archivo al almacenamiento.
        
        Args:
            ruta_local_archivo: Ruta del archivo local
            ruta_destino: Carpeta de destino en el almacenamiento
            
        Returns:
            URL pública del archivo subido
        """
        pass
    
    @abstractmethod
    def archivo_existe(self, ruta_archivo: str) -> bool:
        """Verifica si un archivo existe en el almacenamiento."""
        pass


class INotificationService(ABC):
    """Interfaz para servicios de notificación."""
    
    @abstractmethod
    def enviar_correo_exito(self, **kwargs) -> None:
        """Envía un correo de notificación de éxito."""
        pass
    
    @abstractmethod
    def enviar_correo_error(self, **kwargs) -> None:
        """Envía un correo de notificación de error."""
        pass


class IDataProcessor(ABC):
    """Interfaz para procesadores de datos."""
    
    @abstractmethod
    def procesar_tablas_y_generar_csv(self, tablas_html: list) -> dict:
        """
        Procesa tablas HTML y genera archivo CSV.
        
        Args:
            tablas_html: Lista de tablas HTML
            
        Returns:
            Diccionario con resultado {"ok": bool, "error": str}
        """
        pass
