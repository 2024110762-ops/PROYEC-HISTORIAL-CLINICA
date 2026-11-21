import hashlib
import hmac
import os
import time
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from .integraciones.clientes import IntegracionError
from .integraciones.laboratorio import sincronizar_resultados
from .models import (
    AuditoriaAcceso,
    Consulta,
    Especialidad,
    EstudioImagen,
    IntegracionLog,
    Medico,
    Medicamento,
    Paciente,
    PersonalClinica,
    RecetaElectronica,
    ResultadoLaboratorio,
    RolesClinica,
    Sede,
)
from .services import descifrar


@override_settings(
    SECURE_SSL_REDIRECT=False,
    SESSION_COOKIE_SECURE=False,
    CSRF_COOKIE_SECURE=False,
    PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'],
)
class HistoriaClinicaTests(TestCase):
    def setUp(self):
        cache.clear()
        self.api = APIClient()
        self.cardiologia = Especialidad.objects.create(nombre='Cardiología')
        self.dermatologia = Especialidad.objects.create(nombre='Dermatología')
        self.sede = Sede.objects.create(nombre='Sede Central')
        self.paciente = Paciente.objects.create(
            codigo_historia='HC-0001',
            nombres='Ana',
            apellidos='Pérez',
            dni='12345678',
            correo='ana@example.test',
        )
        self.otro_paciente = Paciente.objects.create(
            codigo_historia='HC-0002',
            nombres='Luis',
            apellidos='Gómez',
            dni='87654321',
        )
        self.admin = User.objects.create_superuser('admin', 'admin@hce.test', 'ClaveSegura123!')
        self.medico_cardio = self._crear_medico('medico_cardio', 'CMP-001', self.cardiologia)
        self.medico_derma = self._crear_medico('medico_derma', 'CMP-002', self.dermatologia)
        self.usuario_paciente = User.objects.create_user('paciente1', password='ClaveSegura123!')
        self.paciente.cuenta = self.usuario_paciente
        self.paciente.save(update_fields=['cuenta'])
        self.usuario_lab = User.objects.create_user('laboratorista', password='ClaveSegura123!')
        PersonalClinica.objects.create(
            codigo_empleado='EMP-001',
            nombres='Laura',
            apellidos='Lab',
            rol=RolesClinica.LABORATORIO,
            sede=self.sede,
            cuenta=self.usuario_lab,
        )
        self.consulta_cardio = self._crear_consulta(self.paciente, self.medico_cardio, self.cardiologia)
        self.consulta_derma = self._crear_consulta(self.paciente, self.medico_derma, self.dermatologia)

    def _crear_medico(self, nombre, cmp, especialidad):
        usuario = User.objects.create_user(nombre, password='ClaveSegura123!')
        return Medico.objects.create(
            codigo_medico=nombre.upper(),
            nombres=nombre,
            apellidos='Especialista',
            especialidad=especialidad,
            cmp=cmp,
            cuenta=usuario,
        )

    def _crear_consulta(self, paciente, medico, especialidad):
        from django.utils import timezone

        return Consulta.objects.create(
            paciente=paciente,
            medico=medico,
            especialidad=especialidad,
            fecha_hora=timezone.now(),
            motivo='Control',
            sede=self.sede,
        )

    def _autenticar(self, nombre):
        respuesta = self.api.post('/api/login/', {'username': nombre, 'password': 'ClaveSegura123!'})
        self.assertEqual(respuesta.status_code, 200, respuesta.data)
        self.api.credentials(HTTP_AUTHORIZATION=f'Token {respuesta.data["token"]}')
        return respuesta.data

    # Casos de aceptación

    def test_salud_y_listado_de_recursos(self):
        self.assertEqual(self.api.get('/api/health/').status_code, 200)
        self._autenticar('admin')
        respuesta = self.api.get('/api/')
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn('pacientes', respuesta.data)

    def test_raiz_redirige_a_la_api(self):
        respuesta = self.api.get('/')
        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(respuesta['Location'], '/api/')

    def test_login_y_perfil_devuelven_rol_y_especialidad(self):
        perfil = self._autenticar('medico_cardio')
        self.assertEqual(perfil['rol'], 'MEDICO')
        self.assertEqual(perfil['especialidad'], 'Cardiología')
        respuesta = self.api.get('/api/perfil/')
        self.assertEqual(respuesta.data['rol'], 'MEDICO')
        self.assertEqual(respuesta.data['especialidad'], 'Cardiología')

    def test_medico_no_ve_consultas_de_otra_especialidad(self):
        self._autenticar('medico_cardio')
        lista = self.api.get('/api/consultas/')
        self.assertEqual([item['id'] for item in lista.data], [self.consulta_cardio.id])
        detalle = self.api.get(f'/api/consultas/{self.consulta_derma.id}/')
        self.assertEqual(detalle.status_code, 403)

    def test_medico_no_ve_recetas_de_otra_especialidad(self):
        receta = RecetaElectronica.objects.create(
            consulta=self.consulta_derma,
            paciente=self.paciente,
            medico=self.medico_derma,
            firma_digital='a' * 64,
        )
        self._autenticar('medico_cardio')
        self.assertEqual(self.api.get(f'/api/recetas/{receta.id}/').status_code, 403)
        self.assertEqual(self.api.get('/api/recetas/').data, [])

    def test_paciente_solo_ve_su_historia_y_no_ve_auditoria(self):
        self._autenticar('paciente1')
        lista = self.api.get('/api/pacientes/')
        self.assertEqual(len(lista.data), 1)
        self.assertEqual(lista.data[0]['codigo_historia'], 'HC-0001')
        self.assertEqual(self.api.get('/api/pacientes/HC-0002/').status_code, 403)
        self.assertEqual(self.api.get('/api/auditorias/').status_code, 403)

    def test_auditoria_registra_acceso_y_es_solo_lectura(self):
        self._autenticar('admin')
        antes = AuditoriaAcceso.objects.count()
        self.api.get(f'/api/pacientes/{self.paciente.codigo_historia}/')
        self.assertTrue(AuditoriaAcceso.objects.filter(accion='CONSULTAR', modulo='Pacientes').exists())
        self.assertEqual(AuditoriaAcceso.objects.count(), antes + 1)
        registro = AuditoriaAcceso.objects.first()
        with self.assertRaises(ValueError):
            registro.save()

    def test_receta_calcula_firma_y_detalles_anidados(self):
        medicamento = Medicamento.objects.create(nombre='Paracetamol')
        self._autenticar('medico_cardio')
        respuesta = self.api.post(
            '/api/recetas/',
            {
                'consulta': self.consulta_cardio.id,
                'paciente': self.paciente.id,
                'diagnostico': 'Dolor leve',
                'indicaciones': 'Tomar con agua',
                'detalles': [
                    {
                        'medicamento': medicamento.id,
                        'dosis': '500 mg',
                        'frecuencia': 'Cada 8 horas',
                        'duracion': '5 días',
                        'cantidad': 15,
                    }
                ],
            },
            format='json',
        )
        self.assertEqual(respuesta.status_code, 201, respuesta.data)
        receta = RecetaElectronica.objects.get(id=respuesta.data['id'])
        self.assertEqual(len(receta.firma_digital), 64)
        self.assertEqual(receta.detalles.count(), 1)
        self.assertEqual(receta.medico, self.medico_cardio)

    def test_permiso_denegado_se_audita(self):
        self._autenticar('medico_cardio')
        respuesta = self.api.post(
            '/api/recetas/',
            {
                'consulta': self.consulta_derma.id,
                'paciente': self.paciente.id,
                'detalles': [],
            },
            format='json',
        )
        self.assertEqual(respuesta.status_code, 403)
        self.assertTrue(
            AuditoriaAcceso.objects.filter(
                resultado='Denegado', accion='ACCESO_DENEGADO'
            ).exists()
        )

    def test_datos_sensibles_cifrados_en_base_de_datos(self):
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute('SELECT dni FROM historia_paciente WHERE id = %s', [self.paciente.id])
            valor_almacenado = cursor.fetchone()[0]
        self.assertNotEqual(valor_almacenado, '12345678')
        self.assertNotIn('12345678', valor_almacenado)
        self.assertEqual(descifrar(valor_almacenado), '12345678')

    def test_sincronizacion_idempotente(self):
        datos = [
            {
                'codigo_externo': 'LAB-100',
                'codigo_historia': 'HC-0001',
                'tipo_prueba': 'Hemograma',
                'valores': 'Normal',
            }
        ]
        with patch('historia.integraciones.laboratorio.LaboratorioClient.obtener_resultados', return_value=datos):
            primera = sincronizar_resultados()
            segunda = sincronizar_resultados()
        self.assertEqual(primera['creados'], 1)
        self.assertEqual(segunda['actualizados'], 1)
        self.assertEqual(ResultadoLaboratorio.objects.filter(codigo_externo='LAB-100').count(), 1)
        self.assertTrue(IntegracionLog.objects.filter(operacion='SYNC').exists())

    def test_proveedor_fallido_devuelve_503_y_no_toca_datos_locales(self):
        cantidad = ResultadoLaboratorio.objects.count()
        self._autenticar('laboratorista')
        with patch('historia.views.sincronizar_resultados', side_effect=IntegracionError('fallo')):
            respuesta = self.api.post('/api/resultados-laboratorio/sincronizar/')
        self.assertEqual(respuesta.status_code, 503)
        self.assertEqual(ResultadoLaboratorio.objects.count(), cantidad)
        self.assertNotIn('fallo', str(respuesta.data))

    def test_webhook_valida_firma_y_rechaza_replay(self):
        secreto = 'secreto-webhook-de-prueba'
        cuerpo = b'{"codigo_externo":"LAB-100"}'
        marca = str(int(time.time()))
        resumen = hashlib.sha256(cuerpo).hexdigest()
        firma = hmac.new(secreto.encode(), f'{marca}.{resumen}'.encode(), hashlib.sha256).hexdigest()
        self.api.credentials()
        with patch.dict(os.environ, {'WEBHOOK_LAB_SECRET': secreto}):
            with patch('historia.views.sincronizar_resultados', return_value={'total': 0}):
                primera = self.api.post(
                    '/api/webhooks/laboratorio/',
                    cuerpo,
                    content_type='application/json',
                    HTTP_X_HUB_SIGNATURE_256=firma,
                    HTTP_X_WEBHOOK_TIMESTAMP=marca,
                )
                segunda = self.api.post(
                    '/api/webhooks/laboratorio/',
                    cuerpo,
                    content_type='application/json',
                    HTTP_X_HUB_SIGNATURE_256=firma,
                    HTTP_X_WEBHOOK_TIMESTAMP=marca,
                )
        self.assertEqual(primera.status_code, 200)
        self.assertEqual(segunda.status_code, 401)

    def test_exportar_auditoria_tambien_se_audita(self):
        self._autenticar('admin')
        respuesta = self.api.get('/api/auditorias/exportar/')
        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(
            AuditoriaAcceso.objects.filter(accion='EXPORTAR', modulo='Auditoria', resultado='Exito').exists()
        )

    def test_estudios_de_imagen_solo_gestionados_por_imagen(self):
        self._autenticar('laboratorista')
        self.assertEqual(self.api.post('/api/estudios-imagen/sincronizar/').status_code, 403)
        EstudioImagen.objects.create(
            paciente=self.paciente,
            modalidad='RX',
            tipo_estudio='Radiografía de tórax',
        )
        self.assertEqual(EstudioImagen.objects.count(), 1)
