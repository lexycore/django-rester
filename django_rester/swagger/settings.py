import socket

from django.conf import settings
from django_rester.singleton import Singleton


class ResterSwaggerSettings(dict, metaclass=Singleton):

    def __init__(self):
        super().__init__()
        _django_rester_swagger_settings = getattr(settings, 'DJANGO_RESTER_SWAGGER_SETTINGS', {})
        _info = _django_rester_swagger_settings.get('INFO', {})
        _external_docs = _django_rester_swagger_settings.get('EXTERNAL_DOCS', {})
        _info.update({
            'DESCRIPTION': _info.get('DESCRIPTION', ''),
            'VERSION': _info.get('VERSION', '1.0.0'),
            'TITLE': _info.get('TITLE', ''),
            'TERMSOFSERVICE': _info.get('TERMSOFSERVICE', ''),
            'CONTACT': _info.get('CONTACT', {}),
            'LICENCE': _info.get('LICENCE', {}),
        })
        _external_docs.update({
            'DESCRIPTION': _external_docs.get('DESCRIPTION', ''),
            'URL': _external_docs.get('URL', ''),
        })
        self.update({'INFO': _info})
        self.update({'EXTERNAL_DOCS': _external_docs})
        self.update({'GENERATE_SWAGGER_FILE': _django_rester_swagger_settings.get('GENERATE_SWAGGER_FILE', False)})
        self.update({'HOST': _django_rester_swagger_settings.get('HOST', self.hostname)})
        self.update({'BASEPATH': _django_rester_swagger_settings.get('BASEPATH')})
        self.update({'SCHEMES': self._check_schemes(_django_rester_swagger_settings.get('SCHEMES', ['http']))})

    @property
    def hostname(self):
        return socket.gethostname()

    @staticmethod
    def _check_schemes(schemes):
        if not (isinstance(schemes, (list, tuple))):
            schemes = [schemes]
        return schemes


rester_swagger_settings = ResterSwaggerSettings()
