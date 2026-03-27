"""
Helper para procesamiento de datos y transformaciones.
"""
import pandas as pd
import os
import re
import csv
import time
import logging
from pathlib import Path
from playwright.async_api import async_playwright
from datetime import datetime, timedelta
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from dateutil.relativedelta import relativedelta
from io import BytesIO

from app.helpers.resilience import reintentar_accion 


@reintentar_accion(intentos_maximos=3, espera_segundos=2)
async def click_elemento(page, selector, timeout: int = 10000):
    """
    Intenta hacer clic. Si el elemento no está, espera y reintenta.
    """
    await page.wait_for_selector(selector, state="visible", timeout=timeout)
    await page.click(selector)
    print(f"Clic realizado en: {selector}")

async def obtener_botones_ingresar(page, htmlTabla, htmlButton):
    """Obtiene botones de una tabla"""
    await page.wait_for_selector(htmlTabla)
    botones = page.locator(htmlButton)
    total = await botones.count()
    return total, botones

def tabla_a_df(tabla):
    """Convierte una tabla HTML a DataFrame de pandas"""
    filas = []
    for tr in tabla.find_all("tr"):
        celdas = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
        if celdas:
            filas.append(celdas)
    return pd.DataFrame(filas)

def leer_csv_con_cabeceras(ruta_csv):
    """Lee un CSV y retorna filas y cabeceras"""
    with open(ruta_csv, newline='', encoding='utf-8') as archivo:
        lector = csv.DictReader(archivo)
        filas = list(lector)
        cabeceras = lector.fieldnames
        return filas, cabeceras

def limpiar_valor(valor):
    """Limpia y formatea valores numéricos"""
    if valor is None:
        return ""

    if isinstance(valor, (int, float)):
        numero = float(valor)
    else:
        valor = str(valor)

        if valor.strip() in ["–", "-", ""]:
            return ""

        # Limpieza formato chileno
        valor = valor.replace("$", "")
        valor = valor.replace(" ", "")
        valor = valor.replace(".", "")
        valor = valor.replace(",", ".")

        try:
            numero = float(valor)
        except ValueError:
            return ""

    return numero

def limpia_valor_porcentaje(valor_texto):
    """Limpia valores porcentuales"""
    texto = valor_texto.replace("%", "").replace("R.I.", "").replace(",", ".")
    return texto

def limpia_tildes(valor_texto):
    """Elimina tildes de un texto"""
    texto = valor_texto.replace("Á", "A").replace("É", "E").replace("Í", "I").replace("Ó", "O").replace("Ú", "U")
    return texto

def normalizar_numero(valor):
    """Normaliza números decimales a enteros cuando es posible"""
    if valor is None or valor == "":
        return ""
    if isinstance(valor, float) and valor.is_integer():
        return int(valor)
    return valor

def llenadoDeArchivoCsv(tabla, num_columnas, texto, plantilla_csv, ruta_salida, cabeceras_consolidador, rango):
    """Llena un archivo CSV con datos de tablas procesadas"""
    
    for i in range(rango, len(tabla)):
        texto_item = tabla.iloc[i, 0]
        if texto_item is None or texto_item == '':
            break

        fila_base = {col: "" for col in cabeceras_consolidador}

        # CASO NORMAL (2 COLUMNAS)
        if num_columnas == 2:
            valor_texto = tabla.iloc[i, 1]

            fila = fila_base.copy()
            if "%" in valor_texto:
                fila.update({
                    "periodo_remuneracion": datetime.now().strftime("%Y-%m"),
                    "mes_pago": (datetime.now() + relativedelta(months=1)).strftime("%Y-%m"),
                    "seccion": texto,
                    "sub_seccion": "",
                    "entidad": "",
                    "item": texto_item.replace(":", ""),
                    "valor_num": limpia_valor_porcentaje(valor_texto),
                    "unidad": "CLP",
                    "valor_texto": valor_texto
                })
            else:   
                fila.update({
                    "periodo_remuneracion": datetime.now().strftime("%Y-%m"),
                    "mes_pago": (datetime.now() + relativedelta(months=1)).strftime("%Y-%m"),
                    "seccion": texto,
                    "sub_seccion": "",
                    "entidad": "",
                    "item": texto_item.replace(":", ""),
                    "valor_num": limpiar_valor(valor_texto),
                    "unidad": "CLP",
                    "valor_texto": valor_texto
                })

            plantilla_csv.append(fila)

        # CASO UTM / UTA (3 COLUMNAS)
        elif num_columnas == 3:  
            if "UTM" in texto or "UTA" in texto:
                valor_utm = tabla.iloc[i, 1]
                valor_uta = tabla.iloc[i, 2]

                if texto in "VALOR UTM UTA":
                    texto_final = texto.replace("VALOR UTM UTA", "VALOR UTM/UTA")
                else:
                    texto_final = texto

                # UTM
                fila_utm = fila_base.copy()
                fila_utm.update({
                    "periodo_remuneracion": datetime.now().strftime("%Y-%m"),
                    "mes_pago": (datetime.now() + relativedelta(months=1)).strftime("%Y-%m"),
                    "seccion": texto_final,
                    "sub_seccion": "",
                    "entidad": str(texto_item),
                    "item": "UTM",
                    "valor_num": limpiar_valor(valor_utm),
                    "unidad": "CLP",
                    "valor_texto": valor_utm
                })
            
                # UTA
                fila_uta = fila_base.copy()
                fila_uta.update({
                    "periodo_remuneracion": datetime.now().strftime("%Y-%m"),
                    "mes_pago": (datetime.now() + relativedelta(months=1)).strftime("%Y-%m"),
                    "seccion": texto_final,
                    "sub_seccion": "",
                    "entidad": texto_item,
                    "item": "UTA",
                    "valor_num": limpiar_valor(valor_uta),
                    "unidad": "CLP",
                    "valor_texto": valor_uta
                })

                plantilla_csv.extend([fila_utm, fila_uta])
                break
            
            if "CESANTIA" in texto:
                seccion = texto
                fila_actual = i + 1

                while fila_actual < len(tabla):
                    tipo_contrato = tabla.iloc[fila_actual, 0]

                    if tipo_contrato is None or tipo_contrato == "":
                        break

                    valor_empleador = tabla.iloc[fila_actual, 1]
                    valor_trabajador = tabla.iloc[fila_actual, 2]

                    for rol, valor in [
                        ("Empleador", valor_empleador),
                        ("Trabajador", valor_trabajador)
                    ]:
                        fila = fila_base.copy()
                        fila.update({
                            "periodo_remuneracion": datetime.now().strftime("%Y-%m"),
                            "mes_pago": (datetime.now() + relativedelta(months=1)).strftime("%Y-%m"),
                            "seccion": seccion,
                            "sub_seccion": "",
                            "entidad": rol,
                            "item": tipo_contrato,
                            "valor_num": limpia_valor_porcentaje(valor) if "%" in str(valor) else "",
                            "unidad": "%",
                            "valor_texto": valor
                        })

                        plantilla_csv.append(fila)

                    fila_actual += 1

                break

        # CASO TASA COTIZACIÓN AFP / 5 columnas
        elif num_columnas == 5:
            afp = texto_item 
            print(tabla.iloc[i, 0] + " - " + tabla.iloc[i, 1] + " - " + tabla.iloc[i, 2] + " - " + tabla.iloc[i, 3] + " - " + tabla.iloc[i, 4]) 

            dependientes = [
                ("Cargo del Trabajador", tabla.iloc[i, 1]),
                ("Cargo del Empleador", tabla.iloc[i, 2]),
                ("Total a Pagar (*)", tabla.iloc[i, 3]),
            ]

            independientes = [
                ("(Incluye SIS)", tabla.iloc[i, 4]),
            ]

            # DEPENDIENTES
            for concepto, valor in dependientes:
                fila = fila_base.copy()
                fila.update({
                    "periodo_remuneracion": datetime.now().strftime("%Y-%m"),
                    "mes_pago": (datetime.now() + relativedelta(months=1)).strftime("%Y-%m"),
                    "seccion": texto,
                    "sub_seccion": "Dependientes",
                    "entidad": afp,
                    "item": concepto,
                    "valor_num": limpia_valor_porcentaje(valor),
                    "unidad": "%",
                    "valor_texto": valor
                })
                plantilla_csv.append(fila)

            # INDEPENDIENTES
            for concepto, valor in independientes:
                fila = fila_base.copy()
                fila.update({
                    "periodo_remuneracion": datetime.now().strftime("%Y-%m"),
                    "mes_pago": (datetime.now() + relativedelta(months=1)).strftime("%Y-%m"),
                    "seccion": texto,
                    "sub_seccion": "Independientes",
                    "entidad": afp,
                    "item": concepto,
                    "valor_num": limpia_valor_porcentaje(valor),
                    "unidad": "%",
                    "valor_texto": valor
                })
                plantilla_csv.append(fila)
                
    return plantilla_csv

def cargar_plantilla(ruta_archivo, **kwargs):
    """
    Lee un archivo HTML y reemplaza las variables.
    Si llamas a cargar_plantilla(..., ERROR="Fallo"), buscará {{ERROR}} en el HTML.
    """
    try:
        with open(ruta_archivo, "r", encoding="utf-8") as f:
            contenido = f.read()
        
        # Recorre los argumentos y reemplaza en el texto
        for clave, valor in kwargs.items():
            marcador = f"{{{{{clave}}}}}" 
            contenido = contenido.replace(marcador, str(valor))
            
        return contenido
    except Exception as e:
        print(f"Error leyendo plantilla {ruta_archivo}: {e}")
        return f"Error cargando plantilla. Datos: {kwargs}"

class DataHelper:
    """
    Encapsulador de funciones de procesamiento de datos.
    Facilita el procesamiento de tablas HTML y generación de CSV.
    """
    
    def __init__(self, config, logger: logging.Logger):
        self.config = config
        self.logger = logger
    
    def procesar_tablas_y_generar_csv(self, tablas_html: list) -> dict:
        """
        Procesa las tablas HTML extraídas y genera el archivo CSV de salida.
        
        Args:
            tablas_html: Lista de tablas HTML (objetos BeautifulSoup)
            
        Returns:
            dict con "ok" (bool) y opcionalmente "error" (str)
        """
        try:
            self.logger.info("Procesando tablas HTML...")
            
            # Cabeceras del CSV consolidado
            cabeceras_consolidador = [
                "periodo_remuneracion", "mes_pago", "seccion", "sub_seccion",
                "entidad", "item", "valor_num", "unidad", "valor_texto"
            ]
            
            plantilla_csv = []
            
            
            dfs = {}
            for i, texto in enumerate(self.config.ARREGLO_TEXTOS_TABLAS_A_BUSCAR):
                print(i, texto)
                for tabla in tablas_html:
                    textos = tabla.get_text(" ", strip=True).upper()

                    if texto in textos:
                        dfs["tabla"] = tabla_a_df(tabla)
                        num_columnas = dfs["tabla"].shape[1]

                        if num_columnas > 3:
                            rango = 3
                        else:
                            if "CESANTÍA" in texto:
                                rango = 2
                            else:
                                rango = 1

                        textoLimpio = limpia_tildes(texto)
                        print(dfs["tabla"])

                        llenadoDeArchivoCsv(
                            dfs["tabla"],
                            num_columnas,
                            textoLimpio,
                            plantilla_csv,
                            self.config.RUTA_SALIDA,
                            cabeceras_consolidador,
                            rango
                        )
                        break
 
            # convertir a dataframe
            df_final = pd.DataFrame(plantilla_csv, columns=cabeceras_consolidador)

            # crear CSV en memoria
            buffer = BytesIO()
            df_final.to_csv(buffer, index=False, encoding="utf-8-sig", sep=";")

            buffer.seek(0)

            self.logger.info("CSV generado en memoria correctamente")

            return {
                "ok": True,
                "buffer": buffer
            }
            
        except Exception as e:
            self.logger.error(f"Error procesando tablas: {e}", exc_info=True)
            return {"ok": False, "error": str(e)}
