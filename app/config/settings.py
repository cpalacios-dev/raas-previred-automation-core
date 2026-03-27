"""
Configuración centralizada del proyecto usando Pydantic Settings.
Permite cargar configuración desde variables de entorno y overlays.
"""
import os
import yaml
from functools import lru_cache
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings
from dataclasses import field


#def load_overlay_config() -> dict:
#    """Carga configuración desde overlays/{ENV}/.env.yaml"""
#    env = os.getenv("ENV", "dev").lower()
#    # Navega desde config/settings.py hasta la raíz y luego a overlays
#    overlay_path = Path(__file__).resolve().parent.parent / "overlays" / env / ".env.yaml"
#    
#    if overlay_path.exists():
#        with open(overlay_path, 'r', encoding='utf-8') as f:
#            config = yaml.safe_load(f) or {}
#            # Convertir a variables de entorno para que Pydantic las lea
#            for key, value in config.items():
#                if key not in os.environ:
#                    os.environ[str(key)] = str(value)
#            return config
#    return {}

def load_overlay_config() -> dict:
    env = os.getenv("ENV", "dev").lower()

    #overlay_path = Path(__file__).resolve().parent.parent / "overlays" / env / ".env.yaml"
    overlay_path = Path(__file__).resolve().parent.parent.parent / "overlays" / env / ".env.yaml"
    print("ENV:", env)
    print("Buscando config en:", overlay_path)

    if overlay_path.exists():
        print("Archivo encontrado")
        with open(overlay_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f) or {}

            print("CONFIG CARGADA:", config)

            for key, value in config.items():
                if key not in os.environ:
                    os.environ[str(key)] = str(value)

            return config

    print("NO EXISTE EL ARCHIVO DE CONFIG")
    return {}

class Settings(BaseSettings):
    """Configuración global de la aplicación."""
    
    # --- General ---
    PROCESS_NAME: str = "Actualizacion Parametros Previred"
    DEBUG_MODE: bool = True
    BROWSER_HEADLESS: bool = True  # True para Cloud Run (sin interfaz), False para desarrollo local

    # --- Rutas ---
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    RUTA_SALIDA: Path = BASE_DIR / "data" / "output" / "parametros_previred.csv"
    RUTA_PLANTILLA: Path = BASE_DIR / "templates" / "plantilla.csv"
    RUTA_HTML_EXITO: Path = BASE_DIR / "templates" / "email" / "exito.html"
    RUTA_HTML_ERROR: Path = BASE_DIR / "templates" / "email" / "error_generico.html"

    # --- Previred ---
    PREVIRED_URL: str = "https://www.previred.com/"
    HTML_BOTON_INDICADORES: str = "Indicadores Previsionales"
    ARREGLO_TEXTOS_TABLAS_A_BUSCAR: List[str] = [
        "VALOR UF",
        "VALOR UTM UTA",
        "RENTAS TOPES IMPONIBLES",
        "RENTAS MÍNIMAS IMPONIBLES",
        "TASA COTIZACIÓN AFP",
        "SEGURO SOCIAL",
        "SEGURO DE INVALIDEZ Y SOBREVIVENCIA (SIS)",
        "DISTRIBUCIÓN DEL 7% SALUD, PARA EMPLEADORES AFILIADO A CCAF",
        "SEGURO DE CESANTÍA (AFC)"
    ]
    CABECERAS_POR_DEFECTO: List[str] = ["PARAMETRO", "VALOR", "VIGENCIA"]

    # --- GCP ---
    GCP_PROJECT_ID: str = field(default_factory=lambda: os.getenv("PROJECT_GCP", ""))
    GCS_BUCKET_NAME: str = "gcp-name-bucket"
    GCS_CARPETA_DESTINO: str = "Actualización de Parámetros"
    GCS_CARPETA_BASE: str = "rpa"
    GCS_NOMBRE_ARCHIVO: str = "archivo_consolidado.csv"

    # --- Email (SendGrid) & Proxy ---
    # Nombres de secretos de GCP Secret Manager
    # Para SendGrid, el usuario suele ser "apikey"
    SMTP_USER: str = "apikey" # Secreto: name_secret
    SMTP_PASSWORD: str = ""  # Secreto: name_secret (es la API Key de SendGrid)
    
    # Credenciales del Proxy Corporativo
    PROXY_SERVER: str = ""   # ej: http://proxy.empresa.com:8080
    PROXY_USER: str = ""     # Secreto: (ej. sm_rpa_proxy_user)
    PROXY_PASSWORD: str = "" # Secreto: name_secret

    EMAIL_FROM: str = ""
    EMAIL_TO: str = ""
    EMAIL_CC: str = ""
    EMAIL_SUBJECT: str = "Reporte Robot - Actualización Parámetros Previred"

    def ensure_directories(self) -> None:
        """Crea los directorios necesarios si no existen."""
        self.BASE_DIR.joinpath("data", "output").mkdir(parents=True, exist_ok=True)
        self.BASE_DIR.joinpath("data", "input").mkdir(parents=True, exist_ok=True)
        self.BASE_DIR.joinpath("logs").mkdir(parents=True, exist_ok=True)

@lru_cache()
def get_settings() -> Settings:
    """
    Obtiene la instancia de configuración, cargando overlays primero.
    """
    load_overlay_config()
    settings = Settings()
    settings.ensure_directories()
    return settings
