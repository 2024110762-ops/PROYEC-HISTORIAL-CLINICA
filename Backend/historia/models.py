from django.conf import settings
from django.db import models
from django.utils import timezone

from .services import CampoCifrado, hash_determinista


class RolesClinica(models.TextChoices):
    ADMIN = 'ADMIN', 'Administrador'
    MEDICO = 'MEDICO', 'Médico'
    RECEPCION = 'RECEPCION', 'Recepción'
    ENFERMERIA = 'ENFERMERIA', 'Enfermería'
    LABORATORIO = 'LABORATORIO', 'Laboratorio'
    IMAGEN = 'IMAGEN', 'Imágenes'
    PACIENTE = 'PACIENTE', 'Paciente'


class EstadosConsulta(models.TextChoices):
    PROGRAMADA = 'PROGRAMADA', 'Programada'
    EN_CURSO = 'EN_CURSO', 'En curso'
    FINALIZADA = 'FINALIZADA', 'Finalizada'
    CANCELADA = 'CANCELADA', 'Cancelada'


class Especialidad(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'especialidad'
        verbose_name_plural = 'especialidades'

    def __str__(self):
        return self.nombre


class Sede(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    direccion = models.CharField(max_length=200, blank=True)
    telefono = models.CharField(max_length=30, blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class Paciente(models.Model):
    codigo_historia = models.CharField(max_length=32, unique=True)
    nombres = models.CharField(max_length=120)
    apellidos = models.CharField(max_length=120)
    dni = CampoCifrado(unique=True)
    dni_hash = models.CharField(max_length=64, unique=True, editable=False)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    sexo = models.CharField(max_length=20, blank=True)
    telefono = CampoCifrado(blank=True)
    direccion = CampoCifrado(blank=True)
    correo = models.EmailField(blank=True)
    foto = models.ImageField(upload_to='pacientes/', null=True, blank=True)
    cuenta = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='perfil_paciente',
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'paciente'
        verbose_name_plural = 'pacientes'

    def save(self, *args, **kwargs):
        self.dni_hash = hash_determinista(self.dni)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.codigo_historia} - {self.nombres} {self.apellidos}'


class Medico(models.Model):
    codigo_medico = models.CharField(max_length=32, unique=True)
    nombres = models.CharField(max_length=120)
    apellidos = models.CharField(max_length=120)
    especialidad = models.ForeignKey(Especialidad, on_delete=models.PROTECT, related_name='medicos')
    cmp = models.CharField(max_length=30, blank=True)
    imagen = models.ImageField(upload_to='medicos/', null=True, blank=True)
    cuenta = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='perfil_medico',
        null=True,
        blank=True,
    )

    def __str__(self):
        return f'{self.codigo_medico} - {self.nombres} {self.apellidos}'


class PersonalClinica(models.Model):
    codigo_empleado = models.CharField(max_length=32, unique=True)
    nombres = models.CharField(max_length=120)
    apellidos = models.CharField(max_length=120)
    rol = models.CharField(max_length=30, choices=RolesClinica.choices, default=RolesClinica.RECEPCION)
    sede = models.ForeignKey(Sede, on_delete=models.PROTECT, related_name='personal')
    cuenta = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='perfil_clinica',
        null=True,
        blank=True,
    )

    def __str__(self):
        return f'{self.codigo_empleado} - {self.nombres} {self.apellidos}'


class Administrador(models.Model):
    dni = CampoCifrado(unique=True)
    nombre = models.CharField(max_length=120)
    apellidos = models.CharField(max_length=120)
    contraseña = models.CharField(max_length=255)
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='perfil_administrador',
    )
    estado = models.BooleanField(default=True)
    imagen = models.ImageField(upload_to='administradores/', null=True, blank=True)

    def __str__(self):
        return f'{self.nombre} {self.apellidos}'


class Consulta(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='consultas')
    medico = models.ForeignKey(Medico, on_delete=models.PROTECT, related_name='consultas')
    especialidad = models.ForeignKey(Especialidad, on_delete=models.PROTECT, related_name='consultas')
    fecha_hora = models.DateTimeField(default=timezone.now)
    motivo = models.TextField(blank=True)
    diagnostico = models.TextField(blank=True)
    estado = models.CharField(max_length=20, choices=EstadosConsulta.choices, default=EstadosConsulta.PROGRAMADA)
    sede = models.ForeignKey(Sede, on_delete=models.PROTECT, related_name='consultas')

    def __str__(self):
        return f'Consulta {self.pk} - {self.paciente}'


class Medicamento(models.Model):
    nombre = models.CharField(max_length=150, unique=True)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre


class RecetaElectronica(models.Model):
    consulta = models.ForeignKey(Consulta, on_delete=models.SET_NULL, related_name='recetas', null=True, blank=True)
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='recetas')
    medico = models.ForeignKey(Medico, on_delete=models.PROTECT, related_name='recetas')
    fecha_emision = models.DateTimeField(default=timezone.now)
    diagnostico = models.TextField(blank=True)
    indicaciones = models.TextField(blank=True)
    estado = models.CharField(max_length=20, default='VIGENTE')
    firma_digital = models.CharField(max_length=64, blank=True)
    qr = models.ImageField(upload_to='recetas/', null=True, blank=True)

    def __str__(self):
        return f'Receta {self.pk} - {self.paciente}'


class DetalleReceta(models.Model):
    receta = models.ForeignKey(RecetaElectronica, on_delete=models.CASCADE, related_name='detalles')
    medicamento = models.ForeignKey(Medicamento, on_delete=models.PROTECT, related_name='detalles')
    dosis = models.CharField(max_length=100, blank=True)
    frecuencia = models.CharField(max_length=100, blank=True)
    duracion = models.CharField(max_length=100, blank=True)
    cantidad = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.medicamento} - {self.receta_id}'


class ResultadoLaboratorio(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='resultados_laboratorio')
    consulta = models.ForeignKey(Consulta, on_delete=models.SET_NULL, related_name='resultados_laboratorio', null=True, blank=True)
    codigo_externo = models.CharField(max_length=120, unique=True, null=True, blank=True)
    laboratorio = models.CharField(max_length=120, blank=True)
    tipo_prueba = models.CharField(max_length=150, blank=True)
    fecha_toma = models.DateTimeField(null=True, blank=True)
    fecha_resultado = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=30, default='DISPONIBLE')
    valores = models.TextField(blank=True)
    unidad = models.CharField(max_length=50, blank=True)
    interpretacion = models.TextField(blank=True)
    archivo = models.FileField(upload_to='laboratorio/', null=True, blank=True)
    fuente = models.CharField(max_length=20, default='LOCAL')

    def __str__(self):
        return f'{self.tipo_prueba} - {self.paciente}'


class EstudioImagen(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='estudios_imagen')
    consulta = models.ForeignKey(Consulta, on_delete=models.SET_NULL, related_name='estudios_imagen', null=True, blank=True)
    codigo_externo = models.CharField(max_length=120, unique=True, null=True, blank=True)
    modalidad = models.CharField(max_length=50, blank=True)
    tipo_estudio = models.CharField(max_length=150, blank=True)
    fecha_estudio = models.DateTimeField(null=True, blank=True)
    informe = models.TextField(blank=True)
    imagen = models.ImageField(upload_to='estudios/', null=True, blank=True)
    archivo = models.FileField(upload_to='estudios/', null=True, blank=True)
    fuente = models.CharField(max_length=20, default='LOCAL')
    proveedor = models.CharField(max_length=120, blank=True)

    def __str__(self):
        return f'{self.tipo_estudio} - {self.paciente}'


class AuditoriaAcceso(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='auditorias',
        null=True,
        blank=True,
    )
    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.SET_NULL,
        related_name='auditorias',
        null=True,
        blank=True,
    )
    accion = models.CharField(max_length=40)
    modulo = models.CharField(max_length=60)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    ip = models.CharField(max_length=64, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    resultado = models.CharField(max_length=20, default='Exito')
    detalles = models.CharField(max_length=500, blank=True)

    class Meta:
        verbose_name = 'registro de auditoría'
        verbose_name_plural = 'registros de auditoría'
        ordering = ['-fecha_hora']

    def save(self, *args, **kwargs):
        if self.pk and not kwargs.get('force_insert'):
            raise ValueError('Los registros de auditoría no se pueden modificar.')
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.accion} - {self.modulo} - {self.fecha_hora}'


class IntegracionLog(models.Model):
    sistema = models.CharField(max_length=30)
    operacion = models.CharField(max_length=60)
    codigo_externo = models.CharField(max_length=120, blank=True)
    estado = models.CharField(max_length=20)
    mensaje = models.CharField(max_length=255, blank=True)
    fecha_hora = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'registro de integración'
        verbose_name_plural = 'registros de integración'
        ordering = ['-fecha_hora']

    def __str__(self):
        return f'{self.sistema} - {self.operacion} - {self.estado}'


class Menu(models.Model):
    texto = models.CharField(max_length=100)
    icono = models.CharField(max_length=100, blank=True)
    ruta = models.CharField(max_length=200)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'menú'
        verbose_name_plural = 'menús'
        ordering = ['orden']

    def __str__(self):
        return self.texto
