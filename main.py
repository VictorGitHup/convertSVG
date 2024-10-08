from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse
import os
import uuid
import vtracer
import re
from xml.etree import ElementTree as ET
from datetime import datetime, timedelta
import schedule
import threading
import time
import httpx

app = FastAPI()

UPLOAD_FOLDER = "./uploadedimages"
SVG_FOLDER = "./convertedimages"
BASE_URL = "http://localhost:8000"
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
CLEANUP_INTERVAL_MINUTES = 60  # Intervalo de tiempo para ejecutar la limpieza en minutos
FILE_LIFETIME_MINUTES = 60  # Tiempo de vida de los archivos en minutos

ALLOWED_EXTENSIONS = {'jpeg', 'jpg', 'png'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(SVG_FOLDER):
    os.makedirs(SVG_FOLDER)

def is_allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_image_to_svg(input_path, output_path, **kwargs):
    # Iniciar el registro del tiempo
    start_time = time.time()
    vtracer.convert_image_to_svg_py(input_path, output_path, **kwargs)

    # Finalizar el registro del tiempo y calcular la duración
    end_time = time.time()
    conversion_time = end_time - start_time
    print(f"Tiempo de conversión: {conversion_time} segundos")

def clean_filename(filename):
    return re.sub(r"[^a-zA-Z0-9_.-]", "", filename)

def add_conversion_metadata(svg_path):
    try:
        # Lee el contenido del archivo SVG
        tree = ET.parse(svg_path)
        root = tree.getroot()
        
        # Agrega un nuevo elemento para la fecha y hora de conversión sin espacio de nombres
        conversion_metadata = ET.Element("conversion_metadata")
        root.append(conversion_metadata)
        
        # Añade el atributo al elemento conversion_metadata
        conversion_metadata.set("conversion_datetime", str(datetime.now()))

        # Guarda el archivo SVG actualizado
        tree.write(svg_path)
    except Exception as e:
        # Maneja posibles errores durante la adición de metadatos
        pass

def cleanup_files():
    try:
        current_time = datetime.now()

        # Elimina archivos de subida
        for filename in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            # Verifica la extensión del archivo
            if filename.lower().endswith(tuple(ALLOWED_EXTENSIONS)):
                creation_time = datetime.fromtimestamp(os.path.getctime(file_path))
                if current_time - creation_time > timedelta(minutes=FILE_LIFETIME_MINUTES):
                    os.remove(file_path)

        # Elimina archivos de conversión
        for filename in os.listdir(SVG_FOLDER):
            svg_path = os.path.join(SVG_FOLDER, filename)
            try:
                root = ET.parse(svg_path).getroot()
                conversion_datetime_str = root.find(".//conversion_metadata").attrib["conversion_datetime"]
                conversion_datetime = datetime.strptime(conversion_datetime_str, "%Y-%m-%d %H:%M:%S.%f")
                if current_time - conversion_datetime > timedelta(minutes=FILE_LIFETIME_MINUTES):
                    # Elimina el archivo SVG
                    os.remove(svg_path)

                    # Genera el nombre del archivo original
                    original_filename = f"{filename.rsplit('.', 1)[0]}.png"
                    original_path = os.path.join(UPLOAD_FOLDER, original_filename)
                    
                    # Si el archivo original existe, elimínalo
                    if os.path.exists(original_path):
                        os.remove(original_path)

            except Exception as e:
                # Maneja posibles errores al analizar el archivo SVG
                pass
    except Exception as e:
        # Maneja posibles errores durante la limpieza
        pass

def scheduled_cleanup():
    schedule.every(CLEANUP_INTERVAL_MINUTES).minutes.do(cleanup_files)
    while True:
        schedule.run_pending()
        # Evita el uso excesivo de la CPU
        time.sleep(1)

# Inicia el hilo para la limpieza programada
cleanup_thread = threading.Thread(target=scheduled_cleanup)
cleanup_thread.start()

@app.post("/upload")
async def upload(image: UploadFile = File(...)):
    try:
        # Verifica la extensión del archivo
        if not is_allowed_file(image.filename):
            return JSONResponse(content={"error": "Sólo se permiten archivos .jpeg y .png"}, status_code=400)

        # Verifica el tamaño del archivo
        if image.file.__sizeof__() > MAX_FILE_SIZE_BYTES:
            raise HTTPException(status_code=400, detail="El tamaño del archivo excede el máximo permitido (10 MB)")

        # Limpia el nombre del archivo
        cleaned_filename = clean_filename(image.filename)

        # Genera un ID único para la imagen
        unique_id = str(uuid.uuid4())

        # Guarda la imagen en la carpeta de subidas con el ID único y nombre limpio
        filename = f"{unique_id}_{cleaned_filename}"
        upload_path = os.path.join(UPLOAD_FOLDER, filename)
        with open(upload_path, "wb") as image_file:
            image_file.write(image.file.read())

        # Genera el nombre de archivo para el SVG con el mismo ID único
        svg_filename = f"{unique_id}_{os.path.splitext(cleaned_filename)[0]}.svg"
        svg_path = os.path.join(SVG_FOLDER, svg_filename)

        # Convierte la imagen a SVG utilizando vtracer
        convert_image_to_svg(upload_path, svg_path, colormode='color', mode='spline', hierarchical='stacked', filter_speckle=4, color_precision=6, layer_difference=16, corner_threshold=60, length_threshold=4.0, max_iterations=10, splice_threshold=45, path_precision=3)

        # Agrega metadatos al archivo SVG
        add_conversion_metadata(svg_path)

        # Construye el enlace completo del SVG
        svg_link = f"{BASE_URL}/convertedimages/{svg_filename}"

        return JSONResponse(content={"message": "Imagen cargada y convertida correctamente", "svg_link": svg_link})
    except Exception as e:
        return JSONResponse(content={"error": f"An error occurred: {str(e)}"}, status_code=500)

@app.get("/convertedimages/{svg_filename}")
async def get_svg(svg_filename: str):
    try:
        svg_path = os.path.join(SVG_FOLDER, svg_filename)

        if os.path.exists(svg_path):
            # Asegúrate de que el tipo de contenido sea correcto
            return FileResponse(svg_path, media_type="image/svg+xml", filename=svg_filename)
        else:
            return JSONResponse(content={"error": "SVG no encontrado"}, status_code=404)
    except Exception as e:
        ret
    
async def is_link_active(svg_url: str) -> bool:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.head(svg_url)
            return response.status_code == 200
    except httpx.HTTPError:
        return False

@app.head("/convertedimages/{image_path:path}")
async def handle_head_request(image_path: str):
    svg_url = f"/convertedimages/{image_path}"

    if await is_link_active(svg_url):
        return {"status": "active"}
    else:
        raise HTTPException(status_code=404, detail="Enlace no disponible")
