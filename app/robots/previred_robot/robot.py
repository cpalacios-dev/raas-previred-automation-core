"""
Robot para actualización de parámetros de Previred.
"""
import os
import logging
from pathlib import Path
from datetime import datetime

from app.core import BaseRobot, Task, TaskResult
from app.config import get_settings
from app.helpers import SeleniumHelper, DataHelper
from app.services.gcp_service import GcsService

class PreviredRobot(BaseRobot):
    """
    Robot que automatiza la extracción de parámetros de Previred.
    """
    
    def __init__(self, config, logger: logging.Logger):
        super().__init__(config, logger)
        self.browser_helper = None
        self.gcp_service = None
        self.data_helper = None
    
    def setup(self) -> None:
        """Inicializa los servicios con manejo de errores para GCP."""
        self.logger.info("Configurando servicios del robot...")
        
        # 1. Inicialización segura de GCP
        try:
            self.gcp_service = GcsService(self.config.GCS_BUCKET_NAME, self.config.GCP_PROJECT_ID)
            self.logger.info("✅ Servicio GCP Storage vinculado.")
        except Exception as e:
            # Si fallan las credenciales, el robot no se detiene
            self.logger.warning(f"⚠️ Trabajando en modo LOCAL. No se pudo conectar a GCP: {e}")
            self.gcp_service = None

        # 2. Otros servicios
        self.browser_helper = SeleniumHelper(self.config, self.logger, self.gcp_service)
        self.data_helper = DataHelper(self.config, self.logger)
    
    async def teardown(self) -> None:
        if self.browser_helper:
            await self.browser_helper.cerrar()
    
    async def execute(self, task: Task) -> TaskResult:
        self.logger.info(f"Iniciando proceso: {self.config.PROCESS_NAME}")
    
        try:
            # 1. Extracción Web
            self.logger.info("Navegando y extrayendo tablas desde Previred...")
            tablas_html = await self.browser_helper.navegar_y_extraer_tablas()

            # 2. Procesamiento de Datos
            self.logger.info("Procesando tablas y generando CSV en memoria...")
            resultado_procesamiento = self.data_helper.procesar_tablas_y_generar_csv(tablas_html)

            if not resultado_procesamiento["ok"]:
                raise Exception(f"Fallo en el procesamiento de datos: {resultado_procesamiento['error']}")

            buffer_csv = resultado_procesamiento["buffer"]
            
            # 3. Lógica de Subida Condicional
            ruta_gcp_visual = "Guardado localmente (GCP deshabilitado)"
            url_gcs = None

            if self.gcp_service:
                try:
                    self.logger.info(f"Subiendo archivo a GCS: {self.config.GCS_BUCKET_NAME}...")
                    ahora = datetime.now()
                    anio, mes = ahora.strftime("%Y"), ahora.strftime("%m")
                    
                    ruta_destino = f"{self.config.GCS_CARPETA_BASE}/{anio}/{mes}/{self.config.GCS_CARPETA_DESTINO}/{self.config.GCS_NOMBRE_ARCHIVO}"

                    url_gcs = self.gcp_service.subir_archivo_desde_memoria(buffer_csv, ruta_destino)
                    ruta_gcp_visual = f"gs://{self.config.GCS_BUCKET_NAME}/{ruta_destino}"
                    self.logger.info("✅ Archivo subido a GCS correctamente.")
                except Exception as e_gcs:
                    self.logger.error(f"❌ Error durante la subida a GCS: {e_gcs}")
                    ruta_gcp_visual = f"Error en carga: {e_gcs}"
            else:
                self.logger.info("ℹ️ Omitiendo subida a la nube: Robot configurado en modo Local.")

            self.logger.info("Proceso finalizado correctamente.")

            return TaskResult(
                success=True,
                message="Proceso completado.",
                data={"gcs_path": ruta_gcp_visual, "gcs_url": url_gcs}
            )

        except Exception as e:
            self.logger.error(f"Error crítico: {e}", exc_info=True)
            return TaskResult(success=False, message="Error en el proceso", error=str(e))