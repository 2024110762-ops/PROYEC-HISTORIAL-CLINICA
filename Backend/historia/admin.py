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


@admin.register(AuditoriaAcceso)
class AuditoriaAccesoAdmin(admin.ModelAdmin):
    list_display = ('fecha_hora', 'accion', 'modulo', 'usuario', 'paciente', 'resultado')
    list_filter = ('accion', 'resultado', 'modulo')
    readonly_fields = (
        'usuario', 'paciente', 'accion', 'modulo', 'fecha_hora',
        'ip', 'user_agent', 'resultado', 'detalles',
    )

    def has_add_permission(self, solicitud):
        return False

    def has_change_permission(self, solicitud, objeto=None):
        return False

    def has_delete_permission(self, solicitud, objeto=None):
        return False


@admin.register(IntegracionLog)
class IntegracionLogAdmin(admin.ModelAdmin):
    list_display = ('fecha_hora', 'sistema', 'operacion', 'estado')
    list_filter = ('sistema', 'estado')
    readonly_fields = ('sistema', 'operacion', 'codigo_externo', 'estado', 'mensaje', 'fecha_hora')


admin.site.register(Especialidad)
admin.site.register(Sede)
admin.site.register(Paciente)
admin.site.register(Medico)
admin.site.register(PersonalClinica)
admin.site.register(Consulta)
admin.site.register(RecetaElectronica)
admin.site.register(DetalleReceta)
admin.site.register(Medicamento)
admin.site.register(ResultadoLaboratorio)
admin.site.register(EstudioImagen)
admin.site.register(Menu)
admin.site.register(Administrador)
