from .acciones_pacientes import router as pacientes_router
from .acciones_historia_clinica_resumida import router as historia_clinica_resumida_router
from .acciones_receta import router as receta_router
from .acciones_historia_clinica import router as historia_clinica_router
from .acciones_indicaciones_medicas import router as indicaciones_medicas_router
from .acciones_consulta_diaria import router as consulta_diaria_router
from .acciones_turnos import router as turnos_router
from .acciones_busqueda import router as busqueda_router
from .acciones_estudios import router as estudios_router
from .acciones_admin import router as admin_router
from .paginas import router as paginas_router
from .solicitar_turno_publico import router as solicitar_turno_publico_router

__all__ = [
    "pacientes_router",
    "historia_clinica_resumida_router",
    "receta_router",
    "historia_clinica_router",
    "indicaciones_medicas_router",
    "consulta_diaria_router",
    "turnos_router",
    "busqueda_router",
    "estudios_router",
    "admin_router",
    "paginas_router",
    "solicitar_turno_publico_router",    
]

