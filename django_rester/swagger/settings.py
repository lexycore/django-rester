from django.conf import settings

from django_rester.singleton import Singleton

class ResterSwaggerMainSettings(dict, metaclass=Singleton):

    def __init__(self):
        super().__init__()
        _django_rester_swagger_main_settings = getattr(settings, 'DJANGO_RESTER_SWAGGER_INFO', {})

class ResterSwaggerInfoSettings(dict, metaclass=Singleton):

    def __init__(self):
        super().__init__()
        _django_rester_swagger_info_settings = getattr(settings, 'DJANGO_RESTER_SWAGGER_INFO', {})
        self.update({
            'DESCRIPTION': _django_rester_swagger_info_settings.get('DESCRIPTION', ''),
            'VERSION': _django_rester_swagger_info_settings.get('VERSION', '1.0.0'),
            'TITLE': _django_rester_swagger_info_settings.get('TITLE', ''),
            'TERMSOFSERVICE': _django_rester_swagger_info_settings.get('TERMSOFSERVICE', ''),
            'CONTACT': _django_rester_swagger_info_settings.get('CONTACT', {}),
            'LICENCE': _django_rester_swagger_info_settings.get('LICENCE', {}),
        })


rester_swagger_info_settings = ResterSwaggerInfoSettings()
