import hashlib
import hmac
import json
from functools import lru_cache

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.db import models
from django.utils.text import Truncator


class FernetDeterminista(Fernet):
    """Fernet con IV y marca de tiempo fijos para permitir búsquedas y unicidad."""

    def encrypt(self, datos):
        if isinstance(datos, str):
            datos = datos.encode()
        vector = hmac.new(self._signing_key, datos, hashlib.sha256).digest()[:16]
        return self._encrypt_from_parts(datos, 0, vector)


@lru_cache(maxsize=1)
def _cifrador():
    return FernetDeterminista(settings.FERNET_KEY.encode())


def cifrar(valor):
    if valor is None or valor == '':
        return valor
    return _cifrador().encrypt(str(valor)).decode()


def descifrar(valor):
    if valor is None or valor == '':
        return valor
    try:
        return _cifrador().decrypt(valor.encode()).decode()
    except (InvalidToken, TypeError, ValueError):
        return valor


class CampoCifrado(models.TextField):
    """Campo de texto almacenado cifrado y desencriptado al leer de la base de datos."""

    def get_prep_value(self, valor):
        valor = super().get_prep_value(valor)
        return cifrar(valor)

    def from_db_value(self, valor, expresion, conexion):
        return descifrar(valor)

    def to_python(self, valor):
        if isinstance(valor, str) and valor.startswith('gAAAAA'):
            return descifrar(valor)
        return valor


def hash_determinista(valor):
    return hashlib.sha256(f'{valor}|{settings.FIRMA_SALT}'.encode()).hexdigest()


def cifrar_contrasena(valor):
    return make_password(valor)


def contrasena_coincide(valor, hash_almacenado):
    return check_password(valor, hash_almacenado)


def generar_firma_receta(datos):
    contenido = json.dumps(datos, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
    return hashlib.sha256(f'{settings.FIRMA_SALT}|{contenido}'.encode()).hexdigest()


def obtener_rol(usuario):
    if not usuario or not usuario.is_authenticated:
        return 'ANONIMO'
    if usuario.is_staff:
        return 'ADMIN'
    if hasattr(usuario, 'perfil_paciente'):
        return 'PACIENTE'
    if hasattr(usuario, 'perfil_medico'):
        return 'MEDICO'
    if hasattr(usuario, 'perfil_administrador'):
        return 'ADMIN'
    if hasattr(usuario, 'perfil_clinica'):
        return usuario.perfil_clinica.rol
    return 'USUARIO'


def obtener_perfil(usuario):
    rol = obtener_rol(usuario)
    respuesta = {
        'rol': rol,
        'especialidad': '',
        'nombre': usuario.get_full_name() or usuario.get_username(),
        'sede': '',
        'codigo': '',
    }
    if hasattr(usuario, 'perfil_paciente'):
        perfil = usuario.perfil_paciente
        respuesta.update(
            nombre=f'{perfil.nombres} {perfil.apellidos}'.strip(),
            codigo=perfil.codigo_historia,
        )
    elif hasattr(usuario, 'perfil_medico'):
        perfil = usuario.perfil_medico
        respuesta.update(
            nombre=f'{perfil.nombres} {perfil.apellidos}'.strip(),
            especialidad=perfil.especialidad.nombre,
            codigo=perfil.codigo_medico,
        )
    elif hasattr(usuario, 'perfil_clinica'):
        perfil = usuario.perfil_clinica
        respuesta.update(
            nombre=f'{perfil.nombres} {perfil.apellidos}'.strip(),
            sede=perfil.sede.nombre,
            codigo=perfil.codigo_empleado,
        )
    elif hasattr(usuario, 'perfil_administrador'):
        perfil = usuario.perfil_administrador
        respuesta.update(nombre=f'{perfil.nombre} {perfil.apellidos}'.strip())
    return respuesta


def ip_cliente(request):
    cabecera = request.META.get('HTTP_X_FORWARDED_FOR','')
    if cabecera:
        return cabecera.split(',')[0].strip()[:64]
    return request.META.get('REMOTE_ADDR','')[:64]


def usuario_cliente(request):
    agente = request.META.get('HTTP_USER_AGENT','')
    return Truncator(agente).chars(255)
