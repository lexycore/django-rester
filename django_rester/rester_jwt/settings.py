from datetime import timedelta

DJANGO_RESTER_JWT_DEFAULT = {
    'RESTER_SECRET': 'secret_key',
    'RESTER_EXPIRATION_DELTA': timedelta(seconds=60 * 60 * 24 * 14),
    'RESTER_AUTH_HEADER': 'Authorization',
    'RESTER_AUTH_HEADER_PREFIX': 'JWT',
    'RESTER_ALGORITHM': 'HS256',
    'RESTER_PAYLOAD_LIST': ['username'],
    'RESTER_USE_REDIS': False,
}
