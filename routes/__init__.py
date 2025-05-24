from .acciones_pacientes import router as pacientes_router
from .acciones_historia_resumen import router as historia_resumen_router
from .acciones_receta import router as receta_router

__all__ = [
    "pacientes_router",
    "historia_resumen_router",
    "receta_router",
]

