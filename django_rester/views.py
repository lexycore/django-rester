import json
import logging
from json import JSONDecodeError

from django.http import HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from .decorators import permissions
from .permission import IsAuthenticated
from .status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_400_BAD_REQUEST
from .exceptions import (
    RequestStructureException,
    ResponseError,
    ResponseBadRequestMsgList,
    ResponseOkMessage,
    ResponseFailMessage,
    ResponseStructureException,
    CustomValidationException,
)

from .fields import JSONField
from .settings import rester_settings

logger = logging.getLogger('django_rester')


class BaseAPIView(View):
    auth = rester_settings['AUTH_BACKEND']()
    request_fields, response_fields = {}, {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_data = None

    @classmethod
    def get_login_field(cls):
        return cls.auth.settings.get('LOGIN_FIELD') or rester_settings.get('LOGIN_FIELD')

    @classmethod
    def as_view(cls, **kwargs):
        view = super(BaseAPIView, cls).as_view()
        view.cls = cls
        return csrf_exempt(view)

    @property
    def _common_request_response_structure(self):
        # check if request_fields are common to any http method or not
        common_structure = False
        for key in self.request_fields.keys():
            if key in self._allowed_methods():
                common_structure = True
                break
        return common_structure

    def _set_response(self, _response):
        if isinstance(_response, (list, tuple)) and len(_response) == 2:
            response = _response[0]
            status = _response[1]
        else:
            response = _response
            status = HTTP_200_OK
        if isinstance(response, HttpResponse):
            result = response
        else:
            try:
                pure_response = json.dumps(response)
                content_type = 'application/json'
            except TypeError:
                pure_response = str(response)
                status = HTTP_500_INTERNAL_SERVER_ERROR
                content_type = 'text/plain'
            result = HttpResponse(pure_response, content_type=content_type, status=status)
            result = self._set_cors(result)
        return result

    def _data_validate(self, method, data, fields, exception, exception_message):
        if fields == {}:
            return data, []
        if self._common_request_response_structure:
            structure = fields.get(method, None)
        else:
            structure = fields
        if not structure and method not in rester_settings.get('FIELDS_CHECK_EXCLUDED_METHODS', []):
            raise exception(exception_message)
        structured_data, messages = self._check_json_field(data, structure)
        if not messages:
            try:
                structured_data = self.custom_validation(structured_data)
                assert structured_data is not None, '.custom_validation() should return validated structured data'
            except (AssertionError, CustomValidationException) as exc:
                messages = ['{}'.format(exc)]
        if fields is self.response_fields and rester_settings.get('SOFT_RESPONSE_VALIDATION', False):
            structured_data = self._add_filtered_data(data, structured_data)
        return structured_data, messages

    def _add_filtered_data(self, data, structured_data):
        # recursive function, validates response_data by response_fields
        value = None
        if isinstance(data, dict):
            for data_key, data_value in data.items():
                structured_value = structured_data.get(data_key, None)
                correct_value = structured_value if structured_value else data_value
                val = self._add_filtered_data(data.get(data_key, None), correct_value)
                if val is not None:
                    if value is None:
                        value = {}
                    value[data_key] = val

        elif isinstance(data, (list, tuple)):
            for item in data:
                val = self._add_filtered_data(item, structured_data[0])
                if val is not None:
                    if value is None:
                        value = []
                    value.append(val)
        else:
            value = structured_data if structured_data else data
        return value

    def _check_json_field(self, data, structure, key='', messages=None):
        # recursive function, validates request_data by request_fields
        value = None
        if messages is None:
            messages = []
        if isinstance(structure, JSONField):
            value, msg = structure.validate(key, data)
            messages += msg
        elif isinstance(structure, dict):
            if not isinstance(data, dict):
                messages.append('{} should be a dict instance'.format(key))
            else:
                for sub_key, sub_structure in structure.items():
                    val, msg = self._check_json_field(data.get(sub_key, None), sub_structure, sub_key)
                    if val is not None:
                        if value is None:
                            value = {}
                        value[sub_key] = val
                    else:
                        messages += msg
        elif isinstance(structure, (list, tuple)):
            if not isinstance(data, (list, tuple)):
                messages.append('{} should be a list or a tuple instance'.format(key))
            else:
                for item in data:
                    val, msg = self._check_json_field(item, structure[0], key)
                    if val is not None:
                        if value is None:
                            value = []
                        value.append(val)
                    else:
                        messages += msg
        return value, messages

    def _set_request_data(self, request):
        request_data, messages = None, []
        method = request.method
        if method in self._allowed_methods():
            try:
                if method == 'GET':
                    request_data = json.loads(json.dumps(request.GET)) if request.GET else {}
                elif method in ('POST', 'PUT', 'PATCH'):
                    request_data = json.loads(request.body.decode('utf-8')) if request.body else {}
                elif method in ('OPTIONS', 'HEAD'):
                    request_data = {}
                if not isinstance(request_data, (dict, list)):
                    raise JSONDecodeError
            except JSONDecodeError:
                messages.append('Request data is not json serializable')
        return request_data, messages

    def custom_validation(self, structured_data):
        # This method needs for custom validation
        # Only CustomValidationException must be raised here
        return structured_data or {}

    def dispatch(self, request, *args, **kwargs):
        self.request_data, messages = self._set_request_data(request)
        _response, status = [None], None
        if not messages:
            user, messages = self.auth.authenticate(request)
            if not messages and user:
                request.user = user
            self.request_data, messages_ = self._data_validate(
                request.method, self.request_data, self.request_fields, RequestStructureException,
                'request data structure is not valid, check for documentation or leave blank')
            if messages_:
                messages_ = [{"request": messages_}]
            messages += messages_
            method_name = request.method.lower()
            if not messages:
                if method_name in self.http_method_names:
                    handler = getattr(self, method_name, self.http_method_not_allowed)
                else:
                    handler = self.http_method_not_allowed

                # TODO refactor this somehow
                # if method_name in ('options',):
                #     _response = handler(request, *args, **kwargs)
                # else:
                _response = list(self.try_response(handler, request, *args, **kwargs))
                messages_ = _response.pop()
                if messages_:
                    messages_ = [{"response": messages_}]
                messages = messages + messages_
        if messages:
            _response = [self.set_response_structure(data=_response[0], message=messages),
                         HTTP_400_BAD_REQUEST]
        _response = self._set_response(_response)
        return _response

    def _set_cors(self, result):
        cors_access = rester_settings.get('CORS_ACCESS')
        result['Access-Control-Allow-Headers'] = 'Access-Control-Allow-Origin, Content-Type, Authorization'
        # TODO: multiple domains in CORS_ACCESS
        """
        Sounds like the recommended way to do it is to have your server read the Origin header 
        from the client, compare that to the list of domains you would like to allow, 
        and if it matches, echo the value of the Origin header back to the client 
        as the Access-Control-Allow-Origin header in the response.
        """
        if isinstance(cors_access, str):
            result['Access-Control-Allow-Origin'] = cors_access
        elif cors_access is True:
            result['Access-Control-Allow-Origin'] = '*'
        else:
            result['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return result

    def options(self, request, *args, **kwargs):
        result = super().options(request, *args, **kwargs)
        result = self._set_cors(result)
        return result

    def try_response(self, handler, request, *args, **kwargs):
        message = []
        messages = []
        success = None
        data = None
        logger.debug('Request: [{} {}] {}'.format(request.method, request.path, self.request_data))
        try:
            success = True
            data = handler(request, *args, **kwargs)
            if isinstance(data, HttpResponse):
                response_status = data.status_code
            else:
                response_status = HTTP_200_OK
                if isinstance(data, tuple) and len(data) == 2:
                    response_status = data[1]
                    data = data[0]
                data, messages = self._data_validate(request.method, data, self.response_fields,
                                                     ResponseStructureException,
                                                     'response data structure is not valid, check for documentation or leave blank')
        except ResponseError as err:
            logger.exception('Error in handler for [{}]'.format(request.path))
            response_status = err.response_status
            if isinstance(err, ResponseBadRequestMsgList):
                message = err.messages
            elif isinstance(err, (ResponseOkMessage, ResponseFailMessage)):
                response_status = err.response_status
                message = err.message
                data = err.data
                success = isinstance(err, ResponseOkMessage)
            else:
                message = '{}'.format(err)
        except Exception as err:
            logger.exception('Error in handler for [{}]'.format(request.path))
            message = '{}'.format(err)
            response_status = HTTP_500_INTERNAL_SERVER_ERROR
        if success is not None:
            success = 200 <= response_status <= 299
        _response = self.set_response_structure(data, success, message)
        logger.debug('Response: [{}] {}'.format(response_status, _response))
        return _response, response_status, messages

    def set_response_structure(self, data=None, success=True, message=None):
        if isinstance(data, HttpResponse):
            _response = data
        else:
            response_structure = rester_settings.get('RESPONSE_STRUCTURE', {})
            if response_structure:
                res_data = {'success': success,
                            'message': message or [],
                            'data': data,
                            }
                str_data = dict(response_structure)
                for item in str_data.keys():
                    if str_data[item] in res_data:
                        str_data[item] = res_data[item]
                _response = str_data
            else:
                _response = data
        return _response


class Login(BaseAPIView):
    response_fields = {"POST": {"token": JSONField(required=True, field_type=str)}}
    request_fields = {"POST": {BaseAPIView.get_login_field(): JSONField(required=True, field_type=str),
                               "password": JSONField(required=True, field_type=str)}}

    def post(self, request):
        data, status = self.auth.login(request, self.request_data)
        return data, status


class Logout(BaseAPIView):
    @permissions(IsAuthenticated)
    def get(self, request):
        data, status = self.auth.logout(request, self.request_data)
        return data, status
