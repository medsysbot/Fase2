import os
import tempfile
import imghdr
from typing import Optional, Tuple


def obtener_mime(contenido: bytes) -> Optional[str]:
    """Obtiene el mime type a partir del contenido si es posible."""
    tipo = imghdr.what(None, contenido)
    return f"image/{tipo}" if tipo else None


def guardar_imagen_temporal(contenido: bytes, nombre_archivo: str) -> str:
    """Guarda la imagen en un archivo temporal sin validar su extensión."""
    extension = os.path.splitext(nombre_archivo)[1].lower()
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=extension)
    tmp.write(contenido)
    tmp.close()
    return tmp.name


def descargar_imagen(client, bucket: str, nombre_base: str) -> Tuple[Optional[bytes], Optional[str]]:
    """Descarga la primera imagen cuyo nombre comience con el nombre base."""
    try:
        archivos = client.storage.from_(bucket).list()
        for archivo in archivos:
            nombre = archivo.get("name")
            if nombre and nombre.startswith(nombre_base):
                contenido = client.storage.from_(bucket).download(nombre)
                return contenido, nombre
    except Exception:
        pass
    return None, None


def eliminar_imagen(client, bucket: str, nombre_base: str) -> None:
    """Elimina todas las imágenes que comiencen con el nombre base."""
    try:
        archivos = client.storage.from_(bucket).list()
        for archivo in archivos:
            nombre = archivo.get("name")
            if nombre and nombre.startswith(nombre_base):
                try:
                    client.storage.from_(bucket).remove(nombre)
                except Exception:
                    pass
    except Exception:
        pass


def imagen_existe(client, bucket: str, nombre_base: str) -> bool:
    """Devuelve True si existe una imagen con el nombre base."""
    contenido, _ = descargar_imagen(client, bucket, nombre_base)
    return contenido is not None
