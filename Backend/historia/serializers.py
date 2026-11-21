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
from .services import generar_firma_receta


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
        read_only_fields = ('dni_hash',)


class MedicoSerializer(serializers.ModelSerializer):
    especialidad_nombre = serializers.CharField(source='especialidad.nombre', read_only=True)

    class Meta:
        model = Medico
        fields = '__all__'


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
        read_only_fields = '__all__'


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
        extra_kwargs = {'contraseña': {'write_only': True}}
