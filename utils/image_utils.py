import os
import tempfile
import imghdr
from typing import Optional, Tuple

ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg'}


def _extension_from_bytes(contenido: bytes) -> Optional[str]:
    """Detecta la extensión real a partir del contenido."""
    tipo = imghdr.what(None, contenido)
    if tipo == "jpeg":
        return ".jpg"
    if tipo:
        return f".{tipo}"
    return None


def obtener_mime(contenido: bytes) -> Optional[str]:
    """Obtiene el mime type a partir del contenido."""
    ext = _extension_from_bytes(contenido)
    if ext == ".png":
        return "image/png"
    if ext in {".jpg", ".jpeg"}:
        return "image/jpeg"
    return None


def validar_imagen(contenido: bytes, extension: str) -> bool:
    """Valida que el contenido corresponda a una imagen soportada."""
    real_ext = _extension_from_bytes(contenido)
    if not real_ext or real_ext not in ALLOWED_EXTENSIONS:
        return False
    extension = extension.lower()
    if extension == ".jpeg":
        extension = ".jpg"
    return real_ext == extension

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


def imagen_existe(client, bucket: str, nombre_base: str) -> bool:
    """Devuelve True si existe una imagen con el nombre base."""
    contenido, _ = descargar_imagen(client, bucket, nombre_base)
    return contenido is not None
