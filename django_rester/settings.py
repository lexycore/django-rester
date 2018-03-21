from django.conf import settings

from django_rester.status import HTTP_200_OK
from django_rester.singleton import Singleton


class AuthMock:
    def login(self, request):
        return None, HTTP_200_OK

    def logout(self, request):
        return True, HTTP_200_OK

    def authenticate(self, request):
        return None, []


class ResterSettings(dict, metaclass=Singleton):

    def __init__(self):
        super().__init__()
        _django_rester_settings = getattr(settings, 'DJANGO_RESTER', {})
        self.update({
            'LOGIN_FIELD': _django_rester_settings.get('LOGIN_FIELD', 'username'),
            'RESPONSE_STRUCTURE': self._set_response_structure(
                _django_rester_settings.get('RESPONSE_STRUCTURE', False)),
        })
        self.update({'AUTH_BACKEND': self._get_auth_backend(_django_rester_settings.get('AUTH_BACKEND',
                                                                                        'django_rester.rester_jwt'))})
        self.update(
            {'CORS_ACCESS': _django_rester_settings.get('CORS_ACCESS', False)})  # True, False, "*", hosts_string
        self.update({'FIELDS_CHECK_EXCLUDED_METHODS': _django_rester_settings.get('FIELDS_CHECK_EXCLUDED_METHODS',
                                                                                  ['OPTIONS', 'HEAD'])})
        self.update({'SOFT_RESPONSE_VALIDATION': _django_rester_settings.get('SOFT_RESPONSE_VALIDATION',
                                                                             False)})

    @staticmethod
    def _set_response_structure(structure):
        if isinstance(structure, bool) and structure:
            result = {'success': 'success',
                      'message': 'message',
                      'data': 'data',
                      }
        elif isinstance(structure, dict):
            result = structure
        else:
            result = False
        return result

    @staticmethod
    def _get_auth_backend(auth_backend):
        try:
            tmp = __import__(auth_backend, globals(), locals(), ['Auth'])
            auth = getattr(tmp, 'Auth')
        except (ImportError, AttributeError):
            auth = AuthMock
        return auth


rester_settings = ResterSettings()
