from django.conf import settings

from django_rester.singleton import Singleton


class ResterSettings(dict, metaclass=Singleton):

    def __init__(self):
        super().__init__()
        _django_rester_jwt_settings = getattr(settings, 'DJANGO_RESTER_JWT', {})
        username = _django_rester_jwt_settings.get('LOGIN_FIELD', self.login_field)
        self.update({
            'SECRET': _django_rester_jwt_settings.get('SECRET', 'secret_key'),
            'EXPIRE': _django_rester_jwt_settings.get('EXPIRE', 60 * 60 * 24 * 14),
            'AUTH_HEADER': self._auth_header(_django_rester_jwt_settings.get('AUTH_HEADER', 'Authorization')),
            'AUTH_HEADER_PREFIX': _django_rester_jwt_settings.get('AUTH_HEADER_PREFIX', 'jwt'),
            'ALGORITHM': _django_rester_jwt_settings.get('ALGORITHM', 'HS256'),
            'PAYLOAD_LIST': _django_rester_jwt_settings.get('PAYLOAD_LIST', [username]),
            'USE_REDIS': _django_rester_jwt_settings.get('USE_REDIS', False),
            'LOGIN_FIELD': username,
        })

    @staticmethod
    def _auth_header(header):
        http = 'HTTP_'
        header = str(header).strip().upper()
        return '{}{}'.format('' if header.startswith(http) else http, header)

    @property
    def login_field(self):
        try:
            tmp = __import__('..settings', globals(), locals(), ['rester_settings'])
            result = getattr(tmp, 'rester_settings').get('LOGIN_FIELD', '')
        except (ImportError, AttributeError, TypeError, ValueError):
            result = ''
        return result or 'username'


rester_jwt_settings = ResterSettings()
