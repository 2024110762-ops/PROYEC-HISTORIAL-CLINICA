from django.conf import settings
from django.db import models

from .services import CampoCifrado, cifrar_contrasena, hash_determinista


class RolesClinica(models.TextChoices):
    RECEPCION = 'RECEPCION', 'Recepción'
    ENFERMERIA = 'ENFERMERIA', 'Enfermería'
    LABORATORIO = 'LABORATORIO', 'Laboratorio'
    IMAGEN = 'IMAGEN', 'Imágenes'
    ADMINISTRATIVO = 'ADMINISTRATIVO', 'Administrativo'


class Sexos(models.TextChoices):
    MASCULINO = 'M', 'Masculino'
    FEMENINO = 'F', 'Femenino'
    OTRO = 'O', 'Otro'


class EstadosConsulta(models.TextChoices):
    PROGRAMADA = 'PROGRAMADA', 'Programada'
    EN_CURSO = 'EN_CURSO', 'En curso'
    FINALIZADA = 'FINALIZADA', 'Finalizada'
    CANCELADA = 'CANCELADA', 'Cancelada'


class EstadosReceta(models.TextChoices):
    VIGENTE = 'VIGENTE', 'Vigente'
    ANULADA = 'ANULADA', 'Anulada'


class EstadosResultado(models.TextChoices):
    PENDIENTE = 'PENDIENTE', 'Pendiente'
    DISPONIBLE = 'DISPONIBLE', 'Disponible'
    VALIDADO = 'VALIDADO', 'Validado'


class FuentesDatos(models.TextChoices):
    LOCAL = 'LOCAL', 'Local'
    EXTERNO = 'EXTERNO', 'Externo'


class ResultadosAuditoria(models.TextChoices):
    EXITO = 'Exito', 'Éxito'
    DENEGADO = 'Denegado', 'Denegado'
    ERROR = 'Error', 'Error'


class Especialidad(models.Model):
    nombre = models.CharField(max_length=120, unique=True)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class Sede(models.Model):
    nombre = models.CharField(max_length=120, unique=True)
    direccion = models.CharField(max_length=255, blank=True)
    telefono = models.CharField(max_length=30, blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class Paciente(models.Model):
    codigo_historia = models.CharField(max_length=30, unique=True)
    nombres = models.CharField(max_length=120)
    apellidos = models.CharField(max_length=120)
    dni = CampoCifrado(max_length=255, unique=True)
    dni_hash = models.CharField(max_length=64, unique=True, editable=False)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    sexo = models.CharField(max_length=1, choices=Sexos.choices, blank=True)
    telefono = CampoCifrado(max_length=255, blank=True)
    direccion = CampoCifrado(max_length=255, blank=True)
    correo = CampoCifrado(max_length=255, blank=True)
    foto = models.ImageField(upload_to='pacientes/', blank=True, null=True)
    cuenta = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='perfil_paciente',
    )

    def save(self, *args, **kwargs):
        self.dni_hash = hash_determinista(self.dni or '')
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.codigo_historia} - {self.nombres} {self.apellidos}'


class Medico(models.Model):
    codigo_medico = models.CharField(max_length=30, unique=True)
    nombres = models.CharField(max_length=120)
    apellidos = models.CharField(max_length=120)
    especialidad = models.ForeignKey(Especialidad, on_delete=models.PROTECT, related_name='medicos')
    cmp = CampoCifrado(max_length=255, unique=True)
    imagen = models.ImageField(upload_to='medicos/', blank=True, null=True)
    cuenta = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='perfil_medico',
    )

    def __str__(self):
        return f'Dr(a). {self.nombres} {self.apellidos} ({self.especialidad})'


class PersonalClinica(models.Model):
    codigo_empleado = CampoCifrado(max_length=255)
    nombres = models.CharField(max_length=120)
    apellidos = models.CharField(max_length=120)
    rol = models.CharField(max_length=20, choices=RolesClinica.choices)
    sede = models.ForeignKey(Sede, on_delete=models.PROTECT, related_name='personal')
    cuenta = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='perfil_clinica',
    )

    def __str__(self):
        return f'{self.nombres} {self.apellidos} - {self.get_rol_display()}'


class Consulta(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='consultas')
    medico = models.ForeignKey(Medico, on_delete=models.PROTECT, related_name='consultas')
    especialidad = models.ForeignKey(Especialidad, on_delete=models.PROTECT, related_name='consultas')
    fecha_hora = models.DateTimeField()
    motivo = models.TextField(blank=True)
    diagnostico = models.TextField(blank=True)
    estado = models.CharField(
        max_length=20,
        choices=EstadosConsulta.choices,
        default=EstadosConsulta.PROGRAMADA,
    )
    sede = models.ForeignKey(Sede, on_delete=models.PROTECT, related_name='consultas')

    def __str__(self):
        return f'Consulta {self.especialidad} - {self.paciente} - {self.fecha_hora:%Y-%m-%d %H:%M}'


class RecetaElectronica(models.Model):
    consulta = models.ForeignKey(Consulta, on_delete=models.CASCADE, related_name='recetas')
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='recetas')
    medico = models.ForeignKey(Medico, on_delete=models.PROTECT, related_name='recetas')
    fecha_emision = models.DateTimeField(auto_now_add=True)
    diagnostico = models.TextField(blank=True)
    indicaciones = models.TextField(blank=True)
    estado = models.CharField(max_length=20, choices=EstadosReceta.choices, default=EstadosReceta.VIGENTE)
    firma_digital = models.CharField(max_length=64, editable=False)
    qr = models.ImageField(upload_to='recetas/qr/', blank=True, null=True)

    def __str__(self):
        return f'Receta {self.id} - {self.paciente} - {self.medico}'


class Medicamento(models.Model):
    nombre = models.CharField(max_length=150, unique=True)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre


class DetalleReceta(models.Model):
    receta = models.ForeignKey(RecetaElectronica, on_delete=models.CASCADE, related_name='detalles')
    medicamento = models.ForeignKey(Medicamento, on_delete=models.PROTECT, related_name='detalles')
    dosis = models.CharField(max_length=120)
    frecuencia = models.CharField(max_length=120)
    duracion = models.CharField(max_length=120)
    cantidad = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.medicamento} - {self.dosis} ({self.receta_id})'


class ResultadoLaboratorio(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='resultados_laboratorio')
    consulta = models.ForeignKey(
        Consulta,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resultados_laboratorio',
    )
    codigo_externo = models.CharField(max_length=120, unique=True, null=True, blank=True)
    laboratorio = models.CharField(max_length=150, blank=True)
    tipo_prueba = models.CharField(max_length=150)
    fecha_toma = models.DateTimeField(null=True, blank=True)
    fecha_resultado = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(
        max_length=20,
        choices=EstadosResultado.choices,
        default=EstadosResultado.DISPONIBLE,
    )
    valores = models.TextField(blank=True)
    unidad = models.CharField(max_length=60, blank=True)
    interpretacion = models.TextField(blank=True)
    archivo = models.FileField(upload_to='laboratorio/', blank=True, null=True)
    fuente = models.CharField(max_length=20, choices=FuentesDatos.choices, default=FuentesDatos.LOCAL)

    def __str__(self):
        return f'{self.tipo_prueba} - {self.paciente} ({self.codigo_externo or "local"})'


class EstudioImagen(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='estudios_imagen')
    consulta = models.ForeignKey(
        Consulta,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='estudios_imagen',
    )
    codigo_externo = models.CharField(max_length=120, unique=True, null=True, blank=True)
    modalidad = models.CharField(max_length=80)
    tipo_estudio = models.CharField(max_length=150)
    fecha_estudio = models.DateTimeField(null=True, blank=True)
    informe = models.TextField(blank=True)
    imagen = models.ImageField(upload_to='imagenes/', blank=True, null=True)
    archivo = models.FileField(upload_to='imagenes/archivos/', blank=True, null=True)
    fuente = models.CharField(max_length=20, choices=FuentesDatos.choices, default=FuentesDatos.LOCAL)
    proveedor = models.CharField(max_length=150, blank=True)

    def __str__(self):
        return f'{self.modalidad} - {self.tipo_estudio} - {self.paciente}'


class AuditoriaAcceso(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='auditorias',
    )
    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='auditorias',
    )
    accion = models.CharField(max_length=40)
    modulo = models.CharField(max_length=60)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    ip = models.CharField(max_length=64, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    resultado = models.CharField(
        max_length=20,
        choices=ResultadosAuditoria.choices,
        default=ResultadosAuditoria.EXITO,
    )
    detalles = models.TextField(blank=True)

    class Meta:
        ordering = ['-fecha_hora']
        indexes = [
            models.Index(fields=['-fecha_hora']),
            models.Index(fields=['paciente', '-fecha_hora']),
            models.Index(fields=['usuario', '-fecha_hora']),
            models.Index(fields=['accion', '-fecha_hora']),
        ]

    def save(self, *args, **kwargs):
        if self.pk:
            raise ValueError('Los registros de auditoría son inmutables.')
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.accion} - {self.modulo} - {self.resultado} - {self.fecha_hora:%Y-%m-%d %H:%M}'


class IntegracionLog(models.Model):
    sistema = models.CharField(max_length=60)
    operacion = models.CharField(max_length=80)
    codigo_externo = models.CharField(max_length=120, blank=True)
    estado = models.CharField(max_length=20)
    mensaje = models.TextField(blank=True)
    fecha_hora = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_hora']

    def __str__(self):
        return f'{self.sistema} - {self.operacion} - {self.estado}'


class Menu(models.Model):
    texto = models.CharField(max_length=80)
    icono = models.CharField(max_length=80, blank=True)
    ruta = models.CharField(max_length=160)
    orden = models.IntegerField(default=0)

    class Meta:
        ordering = ['orden', 'id']

    def __str__(self):
        return self.texto


class Administrador(models.Model):
    dni = CampoCifrado(max_length=255, unique=True)
    nombre = models.CharField(max_length=120)
    apellidos = models.CharField(max_length=120)
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='perfil_administrador',
    )
    contraseña = models.CharField(max_length=255)
    estado = models.BooleanField(default=True)
    imagen = models.ImageField(upload_to='administradores/', blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.contraseña and not self.contraseña.startswith(('pbkdf2_', 'argon2', 'bcrypt', 'scrypt')):
            clave_plana = self.contraseña
            self.contraseña = cifrar_contrasena(clave_plana)
            self.usuario.set_password(clave_plana)
            self.usuario.save(update_fields=['password'])
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.nombre} {self.apellidos} - {self.usuario}'
