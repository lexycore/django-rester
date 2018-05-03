from django.apps import apps
from django.db.models.base import ModelBase
from .exceptions import JSONFieldModelTypeError, JSONFieldModelError, JSONFieldValueError


class JSONField:
    types = (int, float, str, bool)

    def __init__(self, field_type=None, required=False, default=None, blank=True, model=None, field=''):
        if field_type not in self.types:
            raise JSONFieldValueError('field_type should be one of: {}'.format(
                str(self.types).replace("<class '", '').replace("'>", '')))
        self.field_type = field_type
        self.required = required or (not blank)
        self.default = default
        self.blank = blank
        self.key = ''
        self.model = self._set_model(model)
        self.field = field

        if model and not field:
            self.field = 'id'

            # if not self.var_type:
            #    raise ValueError('var_type should be specified')

    def check_type(self, value):
        messages = []
        try:
            _value = self.field_type(value)
        except (TypeError, ValueError):
            messages.append('Could not treat {} value `{}` as {}'.format(
                self.key or '', value, self.field_type))
            _value = None
        return _value, messages

    def validate(self, key, value):
        self.key = key
        messages = []
        if self.required and (value is None):
            messages.append('`{}` value is required'.format(key))
        else:
            if not self.blank and value == '':
                messages.append('`{}` value blank is not allowed'.format(key))
            elif (self.default is not None) and (value is None):
                value = self.default
        if messages:
            value = None
        else:
            value, msg = self.check_type(value)
            messages += msg
        return value, messages

    @staticmethod
    def _set_model(model):
        if not model:
            return None
        elif isinstance(model, ModelBase):
            return model
        elif isinstance(model, str):
            try:
                app, _model = model.split('.')
                model = apps.get_model(app, _model)
            except (ValueError, LookupError):
                raise JSONFieldModelError(
                    'model name does not match pattern <application>.<Model> or model does not exist')
            return model
        else:
            raise JSONFieldModelTypeError('wrong model type (NoneType, string or ModelBase allowed)')
