from rest_framework.exceptions import APIException, AuthenticationFailed, PermissionDenied
from rest_framework.views import exception_handler as manejador_base

from .models import AuditoriaAcceso
from .services import ip_cliente, obtener_rol, usuario_cliente

ACCIONES = {
    'list': 'LISTAR',
    'retrieve': 'CONSULTAR',
    'create': 'CREAR',
    'update': 'ACTUALIZAR',
    'partial_update': 'ACTUALIZAR',
    'destroy': 'ELIMINAR',
}


def paciente_del_recurso(objeto):
    if objeto is None:
        return None
    if getattr(objeto, '_meta', None) and objeto._meta.model_name == 'paciente':
        return objeto
    return getattr(objeto, 'paciente', None)


def registrar_evento(request, paciente, accion, modulo, resultado='Exito', detalles=''):
    """Escribe un evento de auditoría sin incluir datos clínicos en los detalles."""
    try:
        usuario = getattr(request, 'user', None)
        AuditoriaAcceso.objects.create(
            usuario=usuario if usuario and usuario.is_authenticated else None,
            paciente=paciente,
            accion=accion[:40],
            modulo=modulo[:60],
            ip=ip_cliente(request) if request else '',
            user_agent=usuario_cliente(request) if request else '',
            resultado=resultado,
            detalles=detalles[:500],
        )
    except Exception:
        return None


def registrar_desde_solicitud(request, accion, modulo, resultado, detalles=''):
    return registrar_evento(request, None, accion, modulo, resultado, detalles)


def manejador_excepciones(excepcion, contexto):
    respuesta = manejador_base(excepcion, contexto)
    solicitud = contexto.get('request')
    vista = contexto.get('view')
    modulo = vista.__class__.__name__ if vista else 'API'
    if isinstance(excepcion, (PermissionDenied, AuthenticationFailed)):
        registrar_desde_solicitud(solicitud, 'ACCESO_DENEGADO', modulo, 'Denegado', 'Permiso insuficiente')
    elif isinstance(excepcion, APIException) and respuesta is not None and respuesta.status_code >= 500:
        registrar_desde_solicitud(solicitud, 'ERROR', modulo, 'Error', 'Error interno')
    return respuesta


class RegistrarAuditoriaMixin:
    """Registra cada acceso a una historia clínica en los métodos del ViewSet."""

    modulo_auditoria = 'HistoriaClinica'

    def get_object(self):
        objeto = super().get_object()
        self._objeto_auditoria = objeto
        return objeto

    def perform_create(self, serializer):
        super().perform_create(serializer)
        self._objeto_auditoria = serializer.instance

    def perform_update(self, serializer):
        super().perform_update(serializer)
        self._objeto_auditoria = serializer.instance

    def perform_destroy(self, instancia):
        self._objeto_auditoria = instancia
        super().perform_destroy(instancia)

    def _registrar(self, solicitud, nombre_accion, resultado='Exito', detalles='', pacientes=None):
        accion = ACCIONES.get(nombre_accion, nombre_accion.upper())
        objetivos = pacientes if pacientes is not None else [paciente_del_recurso(getattr(self, '_objeto_auditoria', None))]
        for paciente in objetivos:
            registrar_evento(solicitud, paciente, accion, self.modulo_auditoria, resultado, detalles)

    def list(self, solicitud, *args, **kwargs):
        respuesta = super().list(solicitud, *args, **kwargs)
        consulta = self.filter_queryset(self.get_queryset())
        vistos = {paciente.pk: paciente for paciente in (paciente_del_recurso(item) for item in consulta) if paciente}
        self._registrar(solicitud, 'list', pacientes=list(vistos.values()))
        return respuesta

    def retrieve(self, solicitud, *args, **kwargs):
        respuesta = super().retrieve(solicitud, *args, **kwargs)
        self._registrar(solicitud, 'retrieve')
        return respuesta

    def create(self, solicitud, *args, **kwargs):
        respuesta = super().create(solicitud, *args, **kwargs)
        self._registrar(solicitud, 'create')
        return respuesta

    def update(self, solicitud, *args, **kwargs):
        respuesta = super().update(solicitud, *args, **kwargs)
        self._registrar(solicitud, 'update')
        return respuesta

    def partial_update(self, solicitud, *args, **kwargs):
        respuesta = super().partial_update(solicitud, *args, **kwargs)
        self._registrar(solicitud, 'partial_update')
        return respuesta

    def destroy(self, solicitud, *args, **kwargs):
        respuesta = super().destroy(solicitud, *args, **kwargs)
        self._registrar(solicitud, 'destroy', pacientes=[None])
        return respuesta


def rol_de_la_solicitud(solicitud):
    return obtener_rol(getattr(solicitud, 'user', None))
