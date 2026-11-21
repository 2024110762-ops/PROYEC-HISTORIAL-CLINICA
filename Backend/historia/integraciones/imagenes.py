from django.db import transaction
from django.utils.dateparse import parse_datetime

from ..models import EstudioImagen, IntegracionLog, Paciente
from .clientes import ImagenClient


def _fecha(valor):
    if not valor:
        return None
    return parse_datetime(str(valor))


def sincronizar_estudios():
    """Sincronización idempotente por código externo con rollback ante errores."""
    cliente = ImagenClient()
    estudios = cliente.obtener_estudios()
    creados = 0
    actualizados = 0
    with transaction.atomic():
        for elemento in estudios:
            codigo = str(elemento.get('codigo_externo', '')).strip()
            if not codigo:
                continue
            paciente = Paciente.objects.filter(codigo_historia=elemento.get('codigo_historia', '')).first()
            if not paciente:
                continue
            datos = {
                'paciente': paciente,
                'modalidad': elemento.get('modalidad', ''),
                'tipo_estudio': elemento.get('tipo_estudio', ''),
                'fecha_estudio': _fecha(elemento.get('fecha_estudio')),
                'informe': elemento.get('informe', ''),
                'fuente': 'EXTERNO',
                'proveedor': elemento.get('proveedor', ''),
            }
            _, fue_creado = EstudioImagen.objects.update_or_create(
                codigo_externo=codigo,
                defaults=datos,
            )
            if fue_creado:
                creados += 1
            else:
                actualizados += 1
        IntegracionLog.objects.create(
            sistema='IMAGENES',
            operacion='SYNC',
            estado='Exito',
            mensaje=f'Sincronización completada: {creados} nuevos, {actualizados} actualizados',
        )
    return {'creados': creados, 'actualizados': actualizados, 'total': creados + actualizados}
