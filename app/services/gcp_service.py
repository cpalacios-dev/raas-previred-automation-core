# services/gcp_service.py
import logging
import os
from google.cloud import storage
from google.api_core.exceptions import GoogleAPICallError

class GcsService:
    """
    Implementación del servicio de almacenamiento para Google Cloud Storage.
    """
    def __init__(self, bucket_name: str, project_id: str = None):
        self.client = None
        self.bucket = None
        self.bucket_name = bucket_name
        
        try:
            if project_id:
                self.client = storage.Client(project=project_id)
            else:
                self.client = storage.Client()
                
            self.bucket = self.client.bucket(self.bucket_name)
            logging.info(f"✅ Servicio GCS configurado: {self.bucket_name}")
        except Exception as e:
            logging.warning(f"⚠️ No se pudo inicializar GCP Storage (Funcionando en modo Local): {e}")

    def subir_archivo(self, ruta_local_archivo: str, carpeta_destino: str) -> str:
        """
        Sube un archivo a una 'carpeta' específica en GCS conservando su nombre original.
        """
        if not self.client or not self.bucket:
            logging.warning("☁️ GCP no disponible. El archivo se mantendrá solo de forma local.")
            return "local_storage_mode"
        try:
            # 1. Obtenemos el nombre del archivo (ej: consolidado.csv) de la ruta local
            nombre_archivo = os.path.basename(ruta_local_archivo)
            
            # 2. Construimos la ruta final (carpeta + nombre archivo)
            # Nota: usamos '/' porque en GCS las rutas son estilo URL/Unix
            ruta_blob_final = f"{carpeta_destino}/{nombre_archivo}"

            bucket = self.client.bucket(self.bucket_name)
            blob = bucket.blob(ruta_blob_final)
            
            blob.upload_from_filename(ruta_local_archivo)
            
            logging.info(f"Subido: {nombre_archivo} -> gs://{self.bucket_name}/{ruta_blob_final}")
            return blob.public_url

        except GoogleAPICallError as e:
            logging.error(f"Error GCS API: {e}", exc_info=True)
            raise ConnectionError(f"Fallo subida GCS: {e}") from e
        except Exception as e:
            logging.error(f"Error general subiendo archivo: {e}", exc_info=True)
            return None
        
    def subir_archivo_desde_memoria(self, buffer, nombre_archivo, content_type=None):
        """
        Sube un archivo a GCS desde memoria (StringIO o BytesIO)
        """
        if not self.bucket:
                    logging.warning(f"⚠️ Cloud Storage no configurado. Omitiendo subida de: {nombre_archivo}")
                    return None

        try:
            # Detectar content_type si no se proporciona
            if content_type is None:
                if nombre_archivo.endswith('.png'):
                    content_type = 'image/png'
                elif nombre_archivo.endswith('.jpg') or nombre_archivo.endswith('.jpeg'):
                    content_type = 'image/jpeg'
                else:
                    content_type = 'text/csv'

            blob = self.bucket.blob(nombre_archivo)

            buffer.seek(0)

            blob.upload_from_file(
                buffer,
                content_type=content_type
            )

            ruta = f"gs://{self.bucket_name}/{nombre_archivo}"

            logging.info(f"Archivo subido desde memoria: {ruta}")

            return ruta

        except Exception as e:
            logging.error(f"Error subiendo archivo desde memoria: {e}", exc_info=True)
            raise