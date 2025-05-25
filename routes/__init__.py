from .acciones_pacientes import router as pacientes_router
from .acciones_historia_resumen import router as historia_resumen_router
from .acciones_receta import router as receta_router
from .acciones_historia_clinica import router as historia_clinica_router
from .acciones_indicaciones import router as indicaciones_router
from .acciones_evolucion import router as evolucion_router
from .acciones_turnos import router as turnos_router
from .acciones_busqueda import router as busqueda_router
from .acciones_estudios import router as estudios_router
from .invitaciones import router as invitaciones_router

__all__ = [
    "pacientes_router",
    "historia_resumen_router",
    "receta_router",
    "historia_clinica_router",
    "indicaciones_router",
    "evolucion_router",
    "turnos_router",
    "busqueda_router",
    "estudios_router",
    "invitaciones_router",
]

