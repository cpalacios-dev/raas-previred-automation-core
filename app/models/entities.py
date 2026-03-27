"""
Entidades de datos del dominio.
Define las estructuras de datos que maneja el sistema.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class ParametroPrevired:
    """Representa un parámetro previred extraído del portal."""
    periodo_remuneracion: str
    mes_pago: str
    seccion: str
    sub_seccion: str
    entidad: str
    item: str
    valor_num: str
    unidad: str
    valor_texto: str
    
    def to_dict(self) -> dict:
        """Convierte la entidad a diccionario."""
        return {
            "periodo_remuneracion": self.periodo_remuneracion,
            "mes_pago": self.mes_pago,
            "seccion": self.seccion,
            "sub_seccion": self.sub_seccion,
            "entidad": self.entidad,
            "item": self.item,
            "valor_num": self.valor_num,
            "unidad": self.unidad,
            "valor_texto": self.valor_texto
        }


@dataclass
class ResultadoProceso:
    """Resultado de la ejecución del proceso."""
    exito: bool
    mensaje: str
    archivo_generado: Optional[str] = None
    ruta_gcs: Optional[str] = None
    url_gcs: Optional[str] = None
    error: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convierte el resultado a diccionario."""
        return {
            "exito": self.exito,
            "mensaje": self.mensaje,
            "archivo_generado": self.archivo_generado,
            "ruta_gcs": self.ruta_gcs,
            "url_gcs": self.url_gcs,
            "error": self.error
        }
