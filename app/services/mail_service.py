import logging
import os
import base64
import requests
import urllib.parse

from app.config.settings import Settings
from app.helpers.data_processing import cargar_plantilla

class EmailService:
    """
    Servicio para el envío de correos electrónicos a través de SendGrid,
    con soporte para proxy corporativo.
    """
    def __init__(self, config: Settings, logger: logging.Logger = None):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        self.sendgrid_url = "https://api.sendgrid.com/v3/mail/send"

    def _get_proxy_config(self) -> dict:
        """Construye la configuración de proxy si es necesario."""
        if not self.config.PROXY_USER or not self.config.PROXY_PASSWORD:
            self.logger.info("No se configuró usuario/password de proxy. Se intentará conexión directa.")
            return None

        # Codificamos la contraseña para evitar errores con caracteres especiales (@, #, etc.)
        safe_password = urllib.parse.quote(self.config.PROXY_PASSWORD)
        
        # Asumimos un host y puerto estándar, puedes añadirlos a settings.py si varían
        proxy_host = "fortiproxy.ing.cl" 
        proxy_port = "8080"
        
        proxy_url = f"http://{self.config.PROXY_USER}:{safe_password}@{proxy_host}:{proxy_port}"
        
        self.logger.info(f"Usando proxy corporativo: http://{self.config.PROXY_USER}:***@{proxy_host}:{proxy_port}")
        
        return {
            "http": proxy_url,
            "https": proxy_url
        }

    def enviar_correo(self, subject: str, body: str, archivo_adjunto: str = None):
        """
        Prepara y envía un correo electrónico usando la API de SendGrid.
        """
        # Preparamos los destinatarios
        lista_to = [{"email": email.strip()} for email in self.config.EMAIL_TO.split(",") if email.strip()]
        lista_cc = [{"email": email.strip()} for email in self.config.EMAIL_CC.split(",") if email.strip()] if self.config.EMAIL_CC else []

        # Construimos el JSON del mensaje
        data = {
            "personalizations": [{"to": lista_to, "subject": subject}],
            "from": {"email": self.config.EMAIL_FROM},
            "content": [{"type": "text/html", "value": body}]
        }

        if lista_cc:
            data["personalizations"][0]["cc"] = lista_cc

        # Lógica de Adjunto
        if archivo_adjunto and os.path.exists(archivo_adjunto):
            try:
                with open(archivo_adjunto, "rb") as f:
                    data_archivo = f.read()
                    data_b64 = base64.b64encode(data_archivo).decode("utf-8")
                
                nombre_archivo = os.path.basename(archivo_adjunto)
                
                data["attachments"] = [{
                    "content": data_b64,
                    "filename": nombre_archivo,
                    "type": "text/csv",
                    "disposition": "attachment"
                }]
                self.logger.info(f"Archivo adjunto preparado: {nombre_archivo}")
            except Exception as e:
                self.logger.error(f"Error preparando adjunto: {e}", exc_info=True)

        # La contraseña SMTP es la API Key de SendGrid
        headers = {
            "Authorization": f"Bearer {self.config.SMTP_PASSWORD}", 
            "Content-Type": "application/json"
        }

        try:
            self.logger.info("Enviando correo vía SendGrid API...")
            proxies = self._get_proxy_config()
            
            response = requests.post(self.sendgrid_url, json=data, headers=headers, proxies=proxies, timeout=60)
            
            response.raise_for_status() # Lanza un error para códigos 4xx/5xx

            self.logger.info(f"Correo enviado correctamente (Status: {response.status_code})")

        except requests.exceptions.RequestException as e:
            self.logger.error("Error crítico al conectar con SendGrid API ", exc_info=True)
            if e.response is not None:
                self.logger.error(f"Respuesta del servidor: {e.response.text}")
            raise

    def enviar_correo_exito(self, ruta_gcp: str, archivo_adjunto: str = None):
        """Envía el correo de notificación de éxito."""
        self.logger.info("Preparando correo de éxito...")
        subject = f"Éxito: {self.config.EMAIL_SUBJECT}"
        
        # Cargar plantilla HTML y reemplazar variables
        body = cargar_plantilla(
            self.config.RUTA_HTML_EXITO,
            PROCESS_NAME=self.config.PROCESS_NAME,
            GCS_PATH=ruta_gcp
        )
        self.enviar_correo(subject, body, archivo_adjunto)

    def enviar_correo_error(self, error: str):
        """Envía el correo de notificación de error."""
        self.logger.info("Preparando correo de error...")
        subject = f"Error: {self.config.EMAIL_SUBJECT}"
        
        body = cargar_plantilla(
            self.config.RUTA_HTML_ERROR,
            ERROR=error
        )
        self.enviar_correo(subject, body)
