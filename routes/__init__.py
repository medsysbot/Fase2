from .acciones_pacientes import router as pacientes_router
from .acciones_historia_clinica_resumida import router as historia_clinica_resumida_router
from .acciones_recetas_medicas import router as recetas_medicas_router
from .acciones_historia_clinica_completa import router as historia_clinica_completa_router
from .acciones_indicaciones_medicas import router as indicaciones_medicas_router
from .acciones_consulta_diaria import router as consulta_diaria_router
from .acciones_enfermeria import router as enfermeria_router
from .acciones_busqueda import router as busqueda_router
from .acciones_registro_pacientes import router as registro_pacientes_router
from .acciones_estudios import router as estudios_router
from .acciones_admin import router as admin_router
from .paginas import router as paginas_router
from .acciones_turnos_pacientes_publico import router as turnos_publicos_router
from .acciones_turnos_pacientes import router as turnos_pacientes_router


__all__ = [
    "pacientes_router",
    "historia_clinica_resumida_router",
    "recetas_medicas_router",
    "historia_clinica_completa_router",
    "indicaciones_medicas_router",
    "consulta_diaria_router",
    "enfermeria_router",
    "busqueda_router",
    "registro_pacientes_router",
    "estudios_router",
    "admin_router",
    "paginas_router",
    "turnos_publicos_router",
    "turnos_pacientes_router",
]

