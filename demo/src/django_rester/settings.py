from .rester_jwt.settings import DJANGO_RESTER_JWT_DEFAULT

DJANGO_RESTER = {
    'RESTER_JWT': DJANGO_RESTER_JWT_DEFAULT,
    'RESTER_LOGIN_FIELD': 'username',
    'RESTER_TRY_RESPONSE_STRUCTURE': False,
    'RESTER_AUTH_BACKEND': 'django_rester.rester_jwt'
}
