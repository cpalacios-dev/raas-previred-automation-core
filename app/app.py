import sys
from pathlib import Path

# Agregar el directorio raíz al path para imports absolutos
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from flask import Flask, jsonify
import threading
import logging
from app.main import iniciar_proceso_parametros

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# Usar un Lock para garantizar la atomicidad al verificar y cambiar el estado
proceso_lock = threading.Lock()
proceso_en_ejecucion = False  # Variable para rastrear el estado


@app.route('/', methods=['GET'])
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint para Cloud Run y monitoreo"""
    return jsonify({
        "status": "healthy",
        "service": "RAAS Pago Remuneraciones - Parámetros Previred",
        "version": "2.0.0",
        "proceso_activo": proceso_en_ejecucion
    }), 200


@app.route('/status', methods=['GET'])
def get_status():
    """Obtener estado actual del proceso"""
    with proceso_lock:
        estado = "en_ejecucion" if proceso_en_ejecucion else "disponible"
    
    return jsonify({
        "estado": estado,
        "proceso_en_ejecucion": proceso_en_ejecucion,
        "mensaje": "El proceso está en ejecución" if proceso_en_ejecucion else "El servicio está disponible"
    }), 200


@app.route('/iniciar-proceso', methods=['POST'])
def iniciar_proceso_endpoint():
    """Endpoint para iniciar el proceso del robot"""
    global proceso_en_ejecucion
    
    with proceso_lock:
        if proceso_en_ejecucion:
            return jsonify({
                "estado": "error",
                "mensaje": "El proceso ya está en ejecución."
            }), 409
        proceso_en_ejecucion = True

    def run_process():
        global proceso_en_ejecucion
        logging.info("Iniciando el proceso completo del robot...")
        try:
            iniciar_proceso_parametros()
        except Exception as e:
            logging.error(f"Error en el proceso: {e}", exc_info=True)
        finally:
            logging.info("El proceso del robot ha finalizado.")
            with proceso_lock:
                proceso_en_ejecucion = False

    # Ejecutar el proceso en un hilo separado para no bloquear la respuesta HTTP
    thread = threading.Thread(target=run_process)
    thread.start()

    return jsonify({
        "estado": "ok",
        "mensaje": "El proceso ha sido iniciado en segundo plano."
    }), 202


if __name__ == '__main__':
    # Escucha en todas las interfaces de red en el puerto 5000
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
