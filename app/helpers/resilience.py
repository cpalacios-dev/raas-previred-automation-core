"""
Módulo de resilencia para reintentar operaciones fallidas.
"""
import time
import functools


def reintentar_accion(intentos_maximos=3, espera_segundos=5):
    """
    Decorador para reintentar una función si falla.
    
    Args:
        intentos_maximos: Número máximo de intentos
        espera_segundos: Segundos a esperar entre intentos
        
    Returns:
        Función decorada con capacidad de reintento
    """
    def decorador(funcion):
        @functools.wraps(funcion)
        def wrapper(*args, **kwargs):
            intentos = 0
            ultimo_error = None

            while intentos < intentos_maximos:
                try:
                    return funcion(*args, **kwargs)
                except Exception as e:
                    ultimo_error = e
                    intentos += 1
                    print(f"Error en '{funcion.__name__}': {str(e)}")
                    
                    if intentos < intentos_maximos:
                        print(f"Reintentando ({intentos}/{intentos_maximos}) en {espera_segundos}s...")
                        time.sleep(espera_segundos)
            
            print(f"Falló '{funcion.__name__}' después de {intentos_maximos} intentos.")
            raise Exception(f"Fallo crítico en {funcion.__name__}: {str(ultimo_error)}")
            
        return wrapper
    return decorador
