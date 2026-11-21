from django.contrib import admin

from .models import (
    Administrador,
    AuditoriaAcceso,
    Consulta,
    DetalleReceta,
    Especialidad,
    EstudioImagen,
    IntegracionLog,
    Medico,
    Medicamento,
    Menu,
    Paciente,
    PersonalClinica,
    RecetaElectronica,
    ResultadoLaboratorio,
    Sede,
)

admin.site.register(
    [
        Administrador,
        AuditoriaAcceso,
        Consulta,
        DetalleReceta,
        Especialidad,
        EstudioImagen,
        IntegracionLog,
        Medico,
        Medicamento,
        Menu,
        Paciente,
        PersonalClinica,
        RecetaElectronica,
        ResultadoLaboratorio,
        Sede,
    ]
)
