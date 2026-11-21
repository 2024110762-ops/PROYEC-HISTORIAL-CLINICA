import hashlib
import hmac
import os
import time

from django.core.cache import cache

VARIABLES_SECRETOS = {
    'laboratorio': 'WEBHOOK_LAB_SECRET',
    'imagenes': 'WEBHOOK_IMAGEN_SECRET',
}
VENTANA_SEGUNDOS = 300


def validar_webhook(sistema, cuerpo, firma, marca_tiempo):
    """Valida HMAC-SHA256, anti-replay por timestamp y evita comparaciones inseguras."""
    secreto = os.getenv(VARIABLES_SECRETOS.get(sistema, ''), '')
    if not secreto or not firma or not marca_tiempo:
        return False
    try:
        instante = int(marca_tiempo)
    except (TypeError, ValueError):
        return False
    if abs(int(time.time()) - instante) > VENTANA_SEGUNDOS:
        return False
    resumen = hashlib.sha256(cuerpo).hexdigest()
    clave_replay = f'webhook:{sistema}:{marca_tiempo}:{resumen}'
    if cache.get(clave_replay):
        return False
    esperada = hmac.new(
        secreto.encode(),
        f'{marca_tiempo}.{resumen}'.encode(),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(esperada, firma):
        return False
    cache.set(clave_replay, True, VENTANA_SEGUNDOS)
    return True
