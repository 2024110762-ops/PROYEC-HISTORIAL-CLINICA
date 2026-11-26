import csv

from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.utils.dateparse import parse_datetime
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, BasePermission, IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.views import APIView

from .auditoria import RegistrarAuditoriaMixin, registrar_desde_solicitud, registrar_evento
from .integraciones.clientes import IntegracionError
from .integraciones.imagenes import sincronizar_estudios
from .integraciones.laboratorio import sincronizar_resultados
from .integraciones.webhooks import validar_webhook
from .models import (
    Administrador,
    AuditoriaAcceso,
    Consulta,
    DetalleReceta,
    EstadosConsulta,
    EstadosReceta,
    Especialidad,
    EstudioImagen,
    Medico,
    Medicamento,
    Menu,
    Paciente,
    PersonalClinica,
    RecetaElectronica,
    ResultadoLaboratorio,
    Sede,
)
from .permissions import (
    EsAdministrador,
    EsMedicoDeLaEspecialidad,
    EsPacienteDelRecurso,
    PuedeGestionarAuditoria,
    PuedeGestionarConsultas,
    PuedeGestionarDetallesReceta,
    PuedeGestionarEstudios,
    PuedeGestionarMaestros,
    PuedeGestionarMedicamentos,
    PuedeGestionarMenu,
    PuedeGestionarPacientes,
    PuedeGestionarRecetas,
    PuedeGestionarResultados,
)
from .serializers import (
    AdministradorSerializer,
    AuditoriaAccesoSerializer,
    ConsultaSerializer,
    DetalleRecetaSerializer,
    EspecialidadSerializer,
    EstudioImagenSerializer,
    MedicoSerializer,
    MedicamentoSerializer,
    MenuSerializer,
    PacienteSerializer,
    PersonalClinicaSerializer,
    RecetaElectronicaSerializer,
    ResultadoLaboratorioSerializer,
    SedeSerializer,
)
from .services import obtener_perfil, obtener_rol


class ControlAccesoMixin:
    validar_especialidad = False
    validar_paciente = False

    def get_permissions(self):
        permisos = [permiso() for permiso in self.permission_classes]
        rol = obtener_rol(self.request.user)
        if self.validar_especialidad and rol == 'MEDICO':
            permisos.append(EsMedicoDeLaEspecialidad())
        if self.validar_paciente and rol == 'PACIENTE':
            permisos.append(EsPacienteDelRecurso())
        return permisos


class PacienteViewSet(RegistrarAuditoriaMixin, ControlAccesoMixin, viewsets.ModelViewSet):
    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer
    permission_classes = [PuedeGestionarPacientes]
    lookup_field = 'codigo_historia'
    modulo_auditoria = 'Pacientes'
    validar_paciente = True

    def get_queryset(self):
        usuario = self.request.user
        rol = obtener_rol(usuario)
        if rol == 'PACIENTE' and self.action == 'list':
            return Paciente.objects.filter(cuenta=usuario)
        if rol == 'MEDICO':
            return Paciente.objects.filter(consultas__especialidad=usuario.perfil_medico.especialidad).distinct()
        return Paciente.objects.all()


class MedicoViewSet(ControlAccesoMixin, viewsets.ModelViewSet):
    queryset = Medico.objects.select_related('especialidad').all()
    serializer_class = MedicoSerializer
    permission_classes = [PuedeGestionarMaestros]


class EspecialidadViewSet(ControlAccesoMixin, viewsets.ModelViewSet):
    queryset = Especialidad.objects.all()
    serializer_class = EspecialidadSerializer
    permission_classes = [PuedeGestionarMaestros]


class SedeViewSet(ControlAccesoMixin, viewsets.ModelViewSet):
    queryset = Sede.objects.all()
    serializer_class = SedeSerializer
    permission_classes = [PuedeGestionarMaestros]


class PersonalClinicaViewSet(ControlAccesoMixin, viewsets.ModelViewSet):
    queryset = PersonalClinica.objects.select_related('sede').all()
    serializer_class = PersonalClinicaSerializer
    permission_classes = [PuedeGestionarMaestros]


class AdministradorViewSet(ControlAccesoMixin, viewsets.ModelViewSet):
    queryset = Administrador.objects.select_related('usuario').all()
    serializer_class = AdministradorSerializer
    permission_classes = [EsAdministrador]


class ConsultaViewSet(RegistrarAuditoriaMixin, ControlAccesoMixin, viewsets.ModelViewSet):
    queryset = Consulta.objects.select_related('paciente', 'medico', 'especialidad', 'sede').all()
    serializer_class = ConsultaSerializer
    permission_classes = [PuedeGestionarConsultas]
    modulo_auditoria = 'Consultas'
    validar_especialidad = True
    validar_paciente = True

    def get_queryset(self):
        usuario = self.request.user
        rol = obtener_rol(usuario)
        if rol == 'PACIENTE':
            return Consulta.objects.filter(paciente__cuenta=usuario)
        if rol == 'MEDICO' and self.action in ('list',):
            return Consulta.objects.filter(especialidad=usuario.perfil_medico.especialidad)
        return Consulta.objects.all()

    def perform_create(self, serializer):
        usuario = self.request.user
        rol = obtener_rol(usuario)
        datos = serializer.validated_data
        if rol == 'MEDICO':
            medico = usuario.perfil_medico
            datos['medico'] = medico
            datos['especialidad'] = medico.especialidad
        elif datos.get('medico') and not datos.get('especialidad'):
            datos['especialidad'] = datos['medico'].especialidad
        super().perform_create(serializer)

    @action(detail=True, methods=['post'], url_path='finalizar')
    def finalizar(self, request, pk=None):
        consulta = self.get_object()
        rol = obtener_rol(request.user)
        if rol == 'MEDICO' and consulta.especialidad_id != request.user.perfil_medico.especialidad_id:
            raise PermissionDenied('No tienes permiso para finalizar esta consulta.')
        if consulta.estado == EstadosConsulta.FINALIZADA:
            return Response({'mensaje': 'No se realizaron cambios'})
        consulta.estado = EstadosConsulta.FINALIZADA
        consulta.save(update_fields=['estado'])
        registrar_evento(request, consulta.paciente, 'ACTUALIZAR', 'Consultas')
        return Response({'mensaje': 'Operación Exitosa'})


class MedicamentoViewSet(ControlAccesoMixin, viewsets.ModelViewSet):
    queryset = Medicamento.objects.all()
    serializer_class = MedicamentoSerializer
    permission_classes = [PuedeGestionarMedicamentos]


class RecetaElectronicaViewSet(RegistrarAuditoriaMixin, ControlAccesoMixin, viewsets.ModelViewSet):
    queryset = RecetaElectronica.objects.select_related('paciente', 'medico', 'consulta').all()
    serializer_class = RecetaElectronicaSerializer
    permission_classes = [PuedeGestionarRecetas]
    modulo_auditoria = 'Recetas'
    validar_especialidad = True
    validar_paciente = True

    def get_queryset(self):
        usuario = self.request.user
        rol = obtener_rol(usuario)
        if rol == 'PACIENTE':
            return RecetaElectronica.objects.filter(paciente__cuenta=usuario)
        if rol == 'MEDICO' and self.action in ('list',):
            return RecetaElectronica.objects.filter(medico__especialidad=usuario.perfil_medico.especialidad)
        return RecetaElectronica.objects.all()

    def perform_create(self, serializer):
        usuario = self.request.user
        if obtener_rol(usuario) == 'MEDICO':
            medico = usuario.perfil_medico
            consulta = serializer.validated_data.get('consulta')
            if consulta and consulta.especialidad_id != medico.especialidad_id:
                raise PermissionDenied('La consulta no pertenece a tu especialidad.')
            serializer.validated_data['medico'] = medico
        super().perform_create(serializer)

    @action(detail=True, methods=['post'], url_path='anular')
    def anular(self, solicitud, pk=None):
        receta = self.get_object()
        if receta.estado == EstadosReceta.ANULADA:
            return Response({'mensaje': 'No se realizaron cambios'})
        receta.estado = EstadosReceta.ANULADA
        receta.save(update_fields=['estado'])
        registrar_evento(solicitud, receta.paciente, 'ANULAR', 'Recetas', 'Exito', f'Receta {receta.pk} anulada')
        return Response({'mensaje': 'Operación Exitosa'})

    def destroy(self, solicitud, *args, **kwargs):
        return self.anular(solicitud, pk=kwargs['pk'])


class DetalleRecetaViewSet(ControlAccesoMixin, viewsets.ModelViewSet):
    queryset = DetalleReceta.objects.select_related('receta', 'medicamento').all()
    serializer_class = DetalleRecetaSerializer
    permission_classes = [PuedeGestionarDetallesReceta]
    validar_especialidad = True

    def get_queryset(self):
        usuario = self.request.user
        rol = obtener_rol(usuario)
        if rol == 'MEDICO':
            return DetalleReceta.objects.filter(receta__medico__especialidad=usuario.perfil_medico.especialidad)
        return DetalleReceta.objects.all()

    def especialidad_del_detalle(self, objeto):
        return objeto.receta.medico.especialidad_id


class ResultadoLaboratorioViewSet(RegistrarAuditoriaMixin, ControlAccesoMixin, viewsets.ModelViewSet):
    queryset = ResultadoLaboratorio.objects.select_related('paciente').all()
    serializer_class = ResultadoLaboratorioSerializer
    permission_classes = [PuedeGestionarResultados]
    modulo_auditoria = 'ResultadosLaboratorio'
    validar_paciente = True

    def get_queryset(self):
        usuario = self.request.user
        rol = obtener_rol(usuario)
        if rol == 'PACIENTE':
            return ResultadoLaboratorio.objects.filter(paciente__cuenta=usuario)
        return ResultadoLaboratorio.objects.all()

    def perform_create(self, serializer):
        if not serializer.validated_data.get('fuente'):
            serializer.validated_data['fuente'] = 'LOCAL'
        super().perform_create(serializer)


class EstudioImagenViewSet(RegistrarAuditoriaMixin, ControlAccesoMixin, viewsets.ModelViewSet):
    queryset = EstudioImagen.objects.select_related('paciente').all()
    serializer_class = EstudioImagenSerializer
    permission_classes = [PuedeGestionarEstudios]
    modulo_auditoria = 'EstudiosImagen'
    validar_paciente = True

    def get_queryset(self):
        usuario = self.request.user
        rol = obtener_rol(usuario)
        if rol == 'PACIENTE':
            return EstudioImagen.objects.filter(paciente__cuenta=usuario)
        return EstudioImagen.objects.all()

    def perform_create(self, serializer):
        if not serializer.validated_data.get('fuente'):
            serializer.validated_data['fuente'] = 'LOCAL'
        super().perform_create(serializer)


class AuditoriaViewSet(ControlAccesoMixin, viewsets.ReadOnlyModelViewSet):
    queryset = AuditoriaAcceso.objects.select_related('usuario', 'paciente').all()
    serializer_class = AuditoriaAccesoSerializer
    permission_classes = [PuedeGestionarAuditoria]

    def get_queryset(self):
        queryset = self.queryset
        parametros = self.request.query_params
        if parametros.get('paciente'):
            queryset = queryset.filter(paciente__codigo_historia=parametros['paciente'])
        if parametros.get('usuario'):
            queryset = queryset.filter(usuario__username=parametros['usuario'])
        if parametros.get('accion'):
            queryset = queryset.filter(accion__icontains=parametros['accion'])
        desde = parse_datetime(parametros.get('desde', '')) if parametros.get('desde') else None
        hasta = parse_datetime(parametros.get('hasta', '')) if parametros.get('hasta') else None
        if desde:
            queryset = queryset.filter(fecha_hora__gte=desde)
        if hasta:
            queryset = queryset.filter(fecha_hora__lte=hasta)
        return queryset

    @action(detail=False, methods=['get'], url_path='exportar')
    def exportar(self, solicitud):
        respuesta = HttpResponse(content_type='text/csv; charset=utf-8')
        respuesta['Content-Disposition'] = 'attachment; filename="auditoria-hce.csv"'
        escritor = csv.writer(respuesta)
        escritor.writerow(['fecha', 'usuario', 'paciente', 'accion', 'modulo', 'ip', 'resultado'])
        for registro in self.get_queryset():
            escritor.writerow(
                [
                    registro.fecha_hora.isoformat(),
                    registro.usuario.get_username() if registro.usuario else '',
                    registro.paciente.codigo_historia if registro.paciente else '',
                    registro.accion,
                    registro.modulo,
                    registro.ip,
                    registro.resultado,
                ]
            )
        registrar_evento(solicitud, None, 'EXPORTAR', 'Auditoria', 'Exito', 'Exportación CSV')
        return respuesta


class MenuViewSet(ControlAccesoMixin, viewsets.ModelViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated()]
        return [EsAdministrador()]


class LoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, solicitud):
        nombre = solicitud.data.get('username') or solicitud.data.get('usuario')
        clave = solicitud.data.get('password') or solicitud.data.get('contraseña')
        usuario = authenticate(username=nombre, password=clave)
        if usuario is None:
            registrar_desde_solicitud(solicitud, 'LOGIN', 'Autenticacion', 'Denegado', 'Credenciales inválidas')
            return Response({'detail': 'Credenciales inválidas.'}, status=status.HTTP_401_UNAUTHORIZED)
        token, _ = Token.objects.get_or_create(user=usuario)
        registrar_evento(solicitud, None, 'LOGIN', 'Autenticacion', 'Exito', 'Inicio de sesión')
        return Response({'token': token.key, **obtener_perfil(usuario)})


class LogoutView(APIView):
    def post(self, solicitud):
        Token.objects.filter(user=solicitud.user).delete()
        registrar_evento(solicitud, None, 'LOGOUT', 'Autenticacion', 'Exito', 'Cierre de sesión')
        return Response({'mensaje': 'Operación Exitosa'})


class PerfilView(APIView):
    def get(self, solicitud):
        return Response(obtener_perfil(solicitud.user))


class HealthView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, solicitud):
        return Response({'status': 'ok'})


class PuedeSincronizarLaboratorio(BasePermission):
    def has_permission(self, solicitud, vista):
        return obtener_rol(solicitud.user) in ('ADMIN', 'LABORATORIO')


class PuedeSincronizarImagenes(BasePermission):
    def has_permission(self, solicitud, vista):
        return obtener_rol(solicitud.user) in ('ADMIN', 'IMAGEN')


class SincronizarLaboratorioView(APIView):
    permission_classes = [PuedeSincronizarLaboratorio]

    def post(self, solicitud):
        try:
            resultado = sincronizar_resultados()
        except IntegracionError:
            return Response(
                {'detail': 'El proveedor externo no está disponible.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        return Response({'mensaje': 'Operación Exitosa', **resultado})


class SincronizarImagenesView(APIView):
    permission_classes = [PuedeSincronizarImagenes]

    def post(self, solicitud):
        try:
            resultado = sincronizar_estudios()
        except IntegracionError:
            return Response(
                {'detail': 'El proveedor externo no está disponible.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        return Response({'mensaje': 'Operación Exitosa', **resultado})


class WebhookBaseView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    sistema = ''

    def post(self, solicitud):
        cuerpo = solicitud.body
        firma = solicitud.META.get('HTTP_X_HUB_SIGNATURE_256', '')
        marca_tiempo = solicitud.META.get('HTTP_X_WEBHOOK_TIMESTAMP', '')
        if not validar_webhook(self.sistema, cuerpo, firma, marca_tiempo):
            registrar_desde_solicitud(solicitud, 'WEBHOOK', 'Integraciones', 'Denegado', 'Firma inválida')
            return Response({'detail': 'Solicitud no autorizada.'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            self.procesar()
        except IntegracionError:
            return Response(
                {'detail': 'El proveedor externo no está disponible.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        return Response({'mensaje': 'Operación Exitosa'})

    def procesar(self):
        raise NotImplementedError


class WebhookLaboratorioView(WebhookBaseView):
    sistema = 'laboratorio'

    def procesar(self):
        sincronizar_resultados()


class WebhookImagenesView(WebhookBaseView):
    sistema = 'imagenes'

    def procesar(self):
        sincronizar_estudios()
