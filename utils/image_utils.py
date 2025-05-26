import os
import tempfile
from typing import Optional, Tuple

ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg'}

def guardar_imagen_temporal(contenido: bytes, nombre_archivo: str) -> str:
    """Guarda la imagen en un archivo temporal con la extension correcta."""
    extension = os.path.splitext(nombre_archivo)[1].lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError("Formato de imagen no soportado para firma o sello")
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=extension)
    tmp.write(contenido)
    tmp.close()
    return tmp.name

def descargar_imagen(client, bucket: str, nombre_base: str) -> Tuple[Optional[bytes], Optional[str]]:
    """Busca y descarga la imagen intentando con las extensiones permitidas."""
    for ext in ALLOWED_EXTENSIONS:
        nombre = f"{nombre_base}{ext}"
        try:
            contenido = client.storage.from_(bucket).download(nombre)
            return contenido, nombre
        except Exception:
            continue
    return None, None

def eliminar_imagen(client, bucket: str, nombre_base: str) -> None:
    """Elimina la imagen si existe para cualquiera de las extensiones permitidas."""
    for ext in ALLOWED_EXTENSIONS:
        try:
            client.storage.from_(bucket).remove(f"{nombre_base}{ext}")
        except Exception:
            pass
