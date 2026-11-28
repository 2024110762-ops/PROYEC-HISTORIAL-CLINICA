from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

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
from .services import generar_codigo_historia, generar_firma_receta


class EspecialidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Especialidad
        fields = '__all__'


class SedeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sede
        fields = '__all__'


class PacienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paciente
        fields = '__all__'
        read_only_fields = ('dni_hash', 'codigo_historia')

    def create(self, datos_validados):
        datos_validados['codigo_historia'] = generar_codigo_historia()
        return super().create(datos_validados)


class MedicoSerializer(serializers.ModelSerializer):
    especialidad_nombre = serializers.CharField(source='especialidad.nombre', read_only=True)
    username = serializers.CharField(write_only=True, required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, required=False, allow_blank=True, style={'input_type': 'password'})

    def to_internal_value(self, datos):
        if 'cuenta' in datos and datos['cuenta'] == '':
            datos = datos.copy()
            datos['cuenta'] = None
        return super().to_internal_value(datos)

    class Meta:
        model = Medico
        fields = '__all__'

    def validate(self, datos):
        username = datos.get('username', '')
        clave = datos.get('password', '')
        if username and not clave:
            raise serializers.ValidationError({'password': 'La contraseña es obligatoria al crear o cambiar de cuenta.'})
        if username and Medico.objects.filter(cuenta__username=username).exclude(pk=getattr(self.instance, 'pk', None)).exists():
            raise serializers.ValidationError({'username': 'Ese usuario ya está asociado a otro médico.'})
        return datos

    def _aplicar_usuario(self, username, clave):
        usuario = get_user_model().objects.filter(username=username).first()
        if usuario and (usuario.is_staff or usuario.is_superuser):
            raise serializers.ValidationError({'username': 'Ese usuario ya es administrador.'})
        if not usuario:
            usuario = get_user_model()(username=username)
        usuario.set_password(clave)
        usuario.is_staff = False
        usuario.is_superuser = False
        usuario.save()
        return usuario

    def create(self, datos_validados):
        username = datos_validados.pop('username', '')
        clave = datos_validados.pop('password', '')
        with transaction.atomic():
            if username:
                datos_validados['cuenta'] = self._aplicar_usuario(username, clave)
            return super().create(datos_validados)

    def update(self, instancia, datos_validados):
        username = datos_validados.pop('username', '')
        clave = datos_validados.pop('password', '')
        with transaction.atomic():
            if username:
                datos_validados['cuenta'] = self._aplicar_usuario(username, clave)
            elif clave and instancia.cuenta_id:
                self._aplicar_usuario(instancia.cuenta.username, clave)
            return super().update(instancia, datos_validados)


class PersonalClinicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalClinica
        fields = '__all__'


class ConsultaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consulta
        fields = '__all__'


class MedicamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicamento
        fields = '__all__'


class DetalleRecetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleReceta
        fields = '__all__'


class DetalleRecetaEscrituraSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleReceta
        fields = ['medicamento', 'dosis', 'frecuencia', 'duracion', 'cantidad']


class RecetaElectronicaSerializer(serializers.ModelSerializer):
    detalles = DetalleRecetaEscrituraSerializer(many=True, required=False)
    firma_digital = serializers.CharField(read_only=True)

    class Meta:
        model = RecetaElectronica
        fields = '__all__'
        read_only_fields = ('firma_digital', 'fecha_emision')
        extra_kwargs = {'medico': {'required': False}}

    def create(self, datos_validados):
        detalles = datos_validados.pop('detalles', [])
        solicitud = self.context.get('request')
        if 'medico' not in datos_validados and solicitud and hasattr(solicitud.user, 'perfil_medico'):
            datos_validados['medico'] = solicitud.user.perfil_medico
        if 'medico' not in datos_validados:
            raise serializers.ValidationError({'medico': 'El médico es obligatorio.'})
        medico = datos_validados.get('medico')
        paciente = datos_validados.get('paciente')
        contenido_firma = {
            'paciente_id': getattr(paciente, 'pk', None),
            'medico_id': getattr(medico, 'pk', None),
            'consulta_id': getattr(datos_validados.get('consulta'), 'pk', None),
            'diagnostico': datos_validados.get('diagnostico', ''),
            'indicaciones': datos_validados.get('indicaciones', ''),
            'detalles': [
                {
                    'medicamento_id': getattr(detalle.get('medicamento'), 'pk', None),
                    'dosis': detalle.get('dosis', ''),
                    'frecuencia': detalle.get('frecuencia', ''),
                }
                for detalle in detalles
            ],
        }
        datos_validados['firma_digital'] = generar_firma_receta(contenido_firma)
        receta = super().create(datos_validados)
        for detalle in detalles:
            DetalleReceta.objects.create(receta=receta, **detalle)
        return receta

    def update(self, instancia, datos_validados):
        detalles = datos_validados.pop('detalles', None)
        receta = super().update(instancia, datos_validados)
        if detalles is not None:
            receta.detalles.all().delete()
            for detalle in detalles:
                DetalleReceta.objects.create(receta=receta, **detalle)
            receta.firma_digital = generar_firma_receta(
                {
                    'receta_id': receta.pk,
                    'diagnostico': receta.diagnostico,
                    'indicaciones': receta.indicaciones,
                    'detalles': [
                        {
                            'medicamento_id': elemento.medicamento_id,
                            'dosis': elemento.dosis,
                            'frecuencia': elemento.frecuencia,
                        }
                        for elemento in receta.detalles.all()
                    ],
                }
            )
            receta.save(update_fields=['firma_digital'])
        return receta


class ResultadoLaboratorioSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultadoLaboratorio
        fields = '__all__'


class EstudioImagenSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstudioImagen
        fields = '__all__'


class AuditoriaAccesoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditoriaAcceso
        fields = '__all__'
        read_only_fields = (
            'id',
            'usuario',
            'paciente',
            'accion',
            'modulo',
            'fecha_hora',
            'ip',
            'user_agent',
            'resultado',
            'detalles',
        )


class IntegracionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntegracionLog
        fields = '__all__'


class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = ['id', 'texto', 'icono', 'ruta', 'orden']


class AdministradorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Administrador
        fields = '__all__'
        extra_kwargs = {
            'contraseña': {'write_only': True, 'required': False, 'allow_blank': True},
        }

    def validate(self, datos_validados):
        if self.instance is None and not datos_validados.get('contraseña'):
            raise serializers.ValidationError({'contraseña': 'Este campo es obligatorio.'})
        return datos_validados

    def update(self, instancia, datos_validados):
        if not datos_validados.get('contraseña'):
            datos_validados.pop('contraseña', None)
        return super().update(instancia, datos_validados)
