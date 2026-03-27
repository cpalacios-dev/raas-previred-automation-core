"""
Helper para manejo de navegador web con Playwright.
"""
import logging
import asyncio
import socket
import os
import ssl
import urllib.request
from pathlib import Path
from datetime import datetime
from io import BytesIO
from playwright.async_api import async_playwright, Page
from bs4 import BeautifulSoup

from app.helpers.resilience import reintentar_accion

class SeleniumHelper:
    """
    Encapsula toda la lógica de interacción con el navegador (Playwright)
    para automatización web.
    """
    def __init__(self, config, logger: logging.Logger, gcs_service=None):
        self.config = config
        self.logger = logger
        self.gcs_service = gcs_service
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def _test_connectivity(self):
        """Test de conectividad TCP + HTTP antes de usar Playwright"""
        try:
            host = "www.previred.com"
            port = 443
            self.logger.info(f"Testing conectividad a {host}:{port}...")
            socket.create_connection((host, port), timeout=10)
            self.logger.info(f"Conectividad a {host} OK")
            return True
        except Exception as e:
            self.logger.error(f"Sin conectividad a {host}: {e}")
            return False

    @reintentar_accion(intentos_maximos=3, espera_segundos=5)
    async def navegar_y_extraer_tablas(self) -> list:
        """
        Inicia el navegador, navega a Previred y extrae las tablas.
        Corregido con await en async_playwright().
        """
        self.logger.info("Iniciando navegador y navegando a Previred...")
        
        try:
            # CORRECCIÓN: Se agrega await al inicio de playwright
            self.playwright = await async_playwright().start()
            
            # Lanzamos el navegador (Chromium)
            self.browser = await self.playwright.chromium.launch(
                headless=self.config.BROWSER_HEADLESS == "true"
            )
            
            self.context = await self.browser.new_context(no_viewport=True)
            self.page = await self.context.new_page()

            # Navegación optimizada a la sección de indicadores
            indicadores_url = f"{self.config.PREVIRED_URL.rstrip('/')}/indicadores-previsionales/"
            self.logger.info(f"Navegando directamente a: {indicadores_url}")
            
            # Aumentamos el timeout y esperamos a que el DOM esté listo
            await self.page.goto(indicadores_url, timeout=60000, wait_until='domcontentloaded')
            
            # Esperamos un momento para asegurar carga de JS dinámico
            await self.page.wait_for_load_state("networkidle")
            self.logger.info("✅ Página de indicadores cargada")

            # Extraemos el HTML y lo procesamos con BeautifulSoup
            html = await self.page.content()
            soup = BeautifulSoup(html, "lxml")
            tablas = soup.find_all("table")

            if not tablas:
                raise Exception("Validación fallida: No se encontraron tablas en el sitio web.")

            self.logger.info(f"Se encontraron {len(tablas)} tablas en la página.")
            return tablas

        except Exception as e:
            self.logger.error(f"Error durante la navegación y extracción: {e}")
            raise

    async def cerrar(self):
        """Cierra todos los recursos de forma segura."""
        self.logger.info("Cerrando navegador...")
        try:
            if self.page: await self.page.close()
            if self.context: await self.context.close()
            if self.browser: await self.browser.close()
            if self.playwright: await self.playwright.stop()
        except Exception as e:
            self.logger.warning(f"Error al cerrar recursos: {e}")
        finally:
            self.playwright = self.browser = self.context = self.page = None
            self.logger.info("Navegador cerrado.")