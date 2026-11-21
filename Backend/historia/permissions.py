from rest_framework.permissions import BasePermission

from .services import obtener_rol

LECTURA = {'list', 'retrieve'}
TODO = '*'


class PermisoPorRecurso(BasePermission):
    """Permisos por rol y acción, con el rol admin representado por `is_staff`."""

    reglas = {}

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        rol = obtener_rol(request.user)
        permitido = self.reglas.get(rol, set())
        return TODO in permitido or getattr(view, 'action', None) in permitido


class EsAdministrador(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class EsMedico(BasePermission):
    def has_permission(self, request, view):
        return obtener_rol(request.user) == 'MEDICO'


class EsRecepcion(BasePermission):
    def has_permission(self, request, view):
        return obtener_rol(request.user) == 'RECEPCION'


class EsEnfermeria(BasePermission):
    def has_permission(self, request, view):
        return obtener_rol(request.user) == 'ENFERMERIA'


class EsLaboratorio(BasePermission):
    def has_permission(self, request, view):
        return obtener_rol(request.user) == 'LABORATORIO'


class EsImagen(BasePermission):
    def has_permission(self, request, view):
        return obtener_rol(request.user) == 'IMAGEN'


class EsPaciente(BasePermission):
    def has_permission(self, request, view):
        return obtener_rol(request.user) == 'PACIENTE'


def especialidad_del_recurso(objeto):
    if hasattr(objeto, 'especialidad_id'):
        return objeto.especialidad_id
    if getattr(objeto, 'medico_id', None):
        return objeto.medico.especialidad_id
    if getattr(objeto, 'consulta_id', None):
        return objeto.consulta.especialidad_id
    if getattr(objeto, 'receta_id', None):
        return objeto.receta.medico.especialidad_id
    return None


class EsMedicoDeLaEspecialidad(BasePermission):
    def has_permission(self, request, view):
        return obtener_rol(request.user) == 'MEDICO'

    def has_object_permission(self, request, view, objeto):
        if obtener_rol(request.user) != 'MEDICO':
            return True
        return especialidad_del_recurso(objeto) == request.user.perfil_medico.especialidad_id


class EsPacienteDelRecurso(BasePermission):
    def has_permission(self, request, view):
        return obtener_rol(request.user) == 'PACIENTE'

    def has_object_permission(self, request, view, objeto):
        if obtener_rol(request.user) != 'PACIENTE':
            return True
        paciente = objeto if getattr(objeto, '_meta', None) and objeto._meta.model_name == 'paciente' else getattr(objeto, 'paciente', None)
        return bool(paciente and paciente.cuenta_id == request.user.id)


class PuedeGestionarPacientes(PermisoPorRecurso):
    reglas = {
        'ADMIN': TODO,
        'RECEPCION': TODO,
        'MEDICO': {'list', 'retrieve', 'update', 'partial_update'},
        'ENFERMERIA': LECTURA,
        'LABORATORIO': LECTURA,
        'IMAGEN': LECTURA,
        'PACIENTE': LECTURA,
    }


class PuedeGestionarConsultas(PermisoPorRecurso):
    reglas = {
        'ADMIN': TODO,
        'MEDICO': TODO,
        'RECEPCION': {'list', 'retrieve', 'create'},
        'ENFERMERIA': LECTURA,
        'LABORATORIO': LECTURA,
        'IMAGEN': LECTURA,
        'PACIENTE': LECTURA,
    }


class PuedeGestionarRecetas(PermisoPorRecurso):
    reglas = {
        'ADMIN': TODO,
        'MEDICO': TODO,
        'PACIENTE': LECTURA,
    }


class PuedeGestionarDetallesReceta(PermisoPorRecurso):
    reglas = {
        'ADMIN': TODO,
        'MEDICO': TODO,
    }


class PuedeGestionarMedicamentos(PermisoPorRecurso):
    reglas = {'ADMIN': TODO, 'MEDICO': LECTURA}


class PuedeGestionarResultados(PermisoPorRecurso):
    reglas = {
        'ADMIN': TODO,
        'LABORATORIO': TODO,
        'MEDICO': LECTURA,
        'IMAGEN': LECTURA,
        'PACIENTE': LECTURA,
    }


class PuedeGestionarEstudios(PermisoPorRecurso):
    reglas = {
        'ADMIN': TODO,
        'IMAGEN': TODO,
        'MEDICO': LECTURA,
        'LABORATORIO': LECTURA,
        'PACIENTE': LECTURA,
    }


class PuedeGestionarAuditoria(PermisoPorRecurso):
    reglas = {'ADMIN': LECTURA | {'exportar'}}


class PuedeGestionarMenu(PermisoPorRecurso):
    reglas = {
        'ADMIN': TODO,
        'MEDICO': LECTURA,
        'RECEPCION': LECTURA,
        'ENFERMERIA': LECTURA,
        'LABORATORIO': LECTURA,
        'IMAGEN': LECTURA,
        'PACIENTE': LECTURA,
    }


class PuedeGestionarMaestros(PermisoPorRecurso):
    reglas = {
        'ADMIN': TODO,
        'MEDICO': LECTURA,
        'RECEPCION': LECTURA,
        'ENFERMERIA': LECTURA,
        'LABORATORIO': LECTURA,
        'IMAGEN': LECTURA,
        'PACIENTE': LECTURA,
    }
