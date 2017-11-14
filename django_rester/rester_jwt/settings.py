from datetime import timedelta

DJANGO_RESTER_JWT_DEFAULT = {
    'JWT_SECRET': 'secret_key',
    'JWT_EXPIRATION_DELTA': timedelta(seconds=60 * 60 * 24 * 14),
    'JWT_AUTH_HEADER': 'Authorization',
    'JWT_AUTH_HEADER_PREFIX': 'JWT',
    'JWT_ALGORITHM': 'HS256',
    'JWT_PAYLOAD_LIST': ['username'],
    'JWT_USE_REDIS': False,
}
