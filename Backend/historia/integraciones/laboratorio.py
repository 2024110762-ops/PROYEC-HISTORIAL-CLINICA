from django.db import transaction
from django.utils.dateparse import parse_datetime

from ..models import IntegracionLog, Paciente, ResultadoLaboratorio
from .clientes import LaboratorioClient


def _fecha(valor):
    if not valor:
        return None
    return parse_datetime(str(valor))


def sincronizar_resultados():
    """Sincronización idempotente por código externo. Las fallas no tocan datos locales."""
    cliente = LaboratorioClient()
    resultados = cliente.obtener_resultados()
    creados = 0
    actualizados = 0
    with transaction.atomic():
        for elemento in resultados:
            codigo = str(elemento.get('codigo_externo', '')).strip()
            if not codigo:
                continue
            paciente = Paciente.objects.filter(codigo_historia=elemento.get('codigo_historia', '')).first()
            if not paciente:
                continue
            datos = {
                'paciente': paciente,
                'laboratorio': elemento.get('laboratorio', ''),
                'tipo_prueba': elemento.get('tipo_prueba', ''),
                'fecha_toma': _fecha(elemento.get('fecha_toma')),
                'fecha_resultado': _fecha(elemento.get('fecha_resultado')),
                'estado': elemento.get('estado', 'DISPONIBLE'),
                'valores': elemento.get('valores', ''),
                'unidad': elemento.get('unidad', ''),
                'interpretacion': elemento.get('interpretacion', ''),
                'fuente': 'EXTERNO',
            }
            _, fue_creado = ResultadoLaboratorio.objects.update_or_create(
                codigo_externo=codigo,
                defaults=datos,
            )
            if fue_creado:
                creados += 1
            else:
                actualizados += 1
        IntegracionLog.objects.create(
            sistema='LABORATORIO',
            operacion='SYNC',
            estado='Exito',
            mensaje=f'Sincronización completada: {creados} nuevos, {actualizados} actualizados',
        )
    return {'creados': creados, 'actualizados': actualizados, 'total': creados + actualizados}
