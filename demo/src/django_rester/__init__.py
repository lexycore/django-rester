def package_defaults(application):
    import sys
    __import__('{}.settings'.format(application))

    DJANGO_RESTER = sys.modules['{}.settings'.format(application)].DJANGO_RESTER
    _settings = sys.modules['django.conf'].settings
    _settings_DJANGO_RESTER = getattr(_settings, 'DJANGO_RESTER', {})

    def compare_dicts(d1, d2):
        for k, v in d1.items():
            if not k in d2:
                d2[k] = v
            else:
                if isinstance(d1[k], dict):
                    compare_dicts(d1[k], d2[k])
        return d2

    def set_auth_backend(rester_settings):
        auth_backend = rester_settings.get('RESTER_AUTH_BACKEND', 'django_rester.rester_jwt.auth')
        if auth_backend:
            rester_settings['RESTER_AUTH_BACKEND'] = sys.modules[rester_settings['RESTER_AUTH_BACKEND']]

        return rester_settings

    new_DJANGO_RESTER = set_auth_backend(compare_dicts(DJANGO_RESTER, _settings_DJANGO_RESTER))
    _settings.DJANGO_RESTER = new_DJANGO_RESTER


package_defaults(__name__)
