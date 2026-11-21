import os
import time

import requests

from ..models import IntegracionLog


class IntegracionError(Exception):
    """Error genérico de proveedor externo; nunca expone credenciales."""


class ClienteBase:
    sistema = 'EXTERNO'
    variable_url = ''
    variable_token = ''

    def __init__(self):
        self.sesion = requests.Session()
        self.timeout = float(os.getenv('INTEGRACION_TIMEOUT', '5'))
        self.reintentos = 3

    @property
    def url_base(self):
        return os.getenv(self.variable_url, '').rstrip('/')

    def cabeceras(self):
        token = os.getenv(self.variable_token, '')
        return {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json',
        }

    def registrar(self, operacion, codigo_externo, estado, mensaje):
        IntegracionLog.objects.create(
            sistema=self.sistema,
            operacion=operacion,
            codigo_externo=codigo_externo[:120],
            estado=estado,
            mensaje=mensaje[:255],
        )

    def obtener(self, operacion, ruta):
        if not self.url_base:
            self.registrar(operacion, '', 'Error', 'Proveedor no configurado')
            raise IntegracionError('El proveedor externo no está disponible.')
        url = f'{self.url_base}{ruta}'
        for intento in range(1, self.reintentos + 1):
            try:
                respuesta = self.sesion.get(url, headers=self.cabeceras(), timeout=self.timeout)
                respuesta.raise_for_status()
                datos = respuesta.json()
                self.registrar(operacion, '', 'Exito', 'Consulta externa correcta')
                return datos
            except (requests.RequestException, ValueError) as exc:
                if intento == self.reintentos:
                    self.registrar(operacion, '', 'Error', f'Fallo del proveedor: {type(exc).__name__}')
                    raise IntegracionError('El proveedor externo no está disponible.') from exc
                time.sleep(0.5 * (2 ** (intento - 1)))


class LaboratorioClient(ClienteBase):
    sistema = 'LABORATORIO'
    variable_url = 'LABORATORIO_URL'
    variable_token = 'LABORATORIO_TOKEN'

    def obtener_resultados(self):
        datos = self.obtener('CONSULTAR_RESULTADOS', '/resultados')
        return datos if isinstance(datos, list) else datos.get('resultados', [])


class ImagenClient(ClienteBase):
    sistema = 'IMAGENES'
    variable_url = 'IMAGENES_URL'
    variable_token = 'IMAGENES_TOKEN'

    def obtener_estudios(self):
        datos = self.obtener('CONSULTAR_ESTUDIOS', '/estudios')
        return datos if isinstance(datos, list) else datos.get('estudios', [])
