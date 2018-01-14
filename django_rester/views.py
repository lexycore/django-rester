import json
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
)

from .fields import JSONField
from .settings import rester_settings


class BaseAPIView(View):
    auth = rester_settings['AUTH_BACKEND']()
    request_fields, response_fields = {}, {}
    response_structure = rester_settings['RESPONSE_STRUCTURE']
    cors_access = rester_settings['CORS_ACCESS']
    excluded_methods = rester_settings['FIELDS_CHECK_EXCLUDED_METHODS']

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

    # @staticmethod
    def _set_response(self, _response):
        if isinstance(_response, tuple) and len(_response) == 2:
            response = _response[0]
            status = _response[1]
        else:
            response = _response
            status = HTTP_200_OK
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

    # def _request_data_validate(self, method, request_data):
    #     if self.request_fields == {}:
    #         return request_data, []
    #
    #     if self._common_request_response_structure:
    #         request_structure = self.request_fields.get(method, None)
    #     else:
    #         request_structure = self.request_fields
    #
    #     if not request_structure:
    #         raise RequestStructureException(
    #             'request data structure is not valid, check for documentation or leave blank')
    #
    #     request_data, messages = self._check_json_field(request_data, request_structure)
    #     return request_data, messages

    # def _response_data_validate(self, method, response_data):
    #     if self.response_fields == {}:
    #         return response_data, []
    #     if self._common_request_response_structure:
    #         response_structure = self.response_fields.get(method, None)
    #     else:
    #         response_structure = self.response_fields
    #     if not response_structure:
    #         raise RequestStructureException(
    #             'response data structure is not valid, check for documentation or leave blank')
    #     response_data, messages = self._check_json_field(response_data, response_structure)
    #     return response_data, messages

    def _data_validate(self, method, data, fields, exception, exception_message):
        if fields == {}:
            return data, []
        if self._common_request_response_structure:
            response_structure = fields.get(method, None)
        else:
            response_structure = fields
        if not response_structure and method not in self.excluded_methods:
            raise exception(exception_message)
        data, messages = self._check_json_field(data, response_structure)
        return data, messages

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
        request_data, messages, message = None, [], 'Request data is not json serializable'
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
                    messages.append(message)
            except JSONDecodeError:
                messages.append(message)
        return request_data, messages

    def dispatch(self, request, *args, **kwargs):
        request_data, messages = self._set_request_data(request)
        _response = None
        if not messages:
            user, messages = self.auth.authenticate(request)
            if not messages and user:
                request.user = user
            # request_data, messages_ = self._request_data_validate(request.method, request_data)
            request_data, messages_ = self._data_validate(
                request.method, request_data, self.request_fields, RequestStructureException,
                'request data structure is not valid, check for documentation or leave blank')
            messages += messages_
            method_name = request.method.lower()
            if not messages:
                if method_name in self.http_method_names:
                    handler = getattr(self, method_name, self.http_method_not_allowed)
                else:
                    handler = self.http_method_not_allowed

                # TODO refactor this somehow
                if method_name in ('options',):
                    _response = handler(request, request_data, *args, **kwargs)
                else:
                    _response = self.try_response(handler, request, request_data, *args, **kwargs)
                    _response = self._set_response(_response)
        if messages:
            _response = self.set_response_structure(None, False, messages)
            _response = self._set_response((_response, HTTP_400_BAD_REQUEST))

        return _response

    def _set_cors(self, result):
        result['Access-Control-Allow-Headers'] = 'Access-Control-Allow-Origin, Content-Type, Authorization'
        if self.cors_access is True:
            result['Access-Control-Allow-Origin'] = '*'
        elif self.cors_access:
            result['Access-Control-Allow-Origin'] = self.cors_access
        else:
            result['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return result

    def options(self, request, *args, **kwargs):
        result = super().options(request, *args, **kwargs)
        result = self._set_cors(result)
        return result

    def try_response(self, handler, request, request_data, *args, **kwargs):
        message = []
        success = None
        data = None
        try:
            success = True
            data = handler(request, request_data, *args, **kwargs)
            response_status = HTTP_200_OK
            if isinstance(data, tuple) and len(data) == 2:
                response_status = data[1]
                data = data[0]
            # data, messages = self._response_data_validate(request.method, data)
            data, messages = self._data_validate(request.method, data, self.response_fields, ResponseStructureException,
                                                 'response data structure is not valid, check for documentation or leave blank')
        except ResponseError as err:
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
            message = '{}'.format(err)
            response_status = HTTP_500_INTERNAL_SERVER_ERROR
        if success is not None:
            success = 200 <= response_status <= 299
        _response = self.set_response_structure(data, success, message)
        return _response, response_status

    def set_response_structure(self, data, success=True, message=None):
        if self.response_structure:
            res_data = {'success': success,
                        'message': message or [],
                        'data': data,
                        }
            str_data = dict(self.response_structure)
            for item in str_data.keys():
                if str_data[item] in res_data:
                    str_data[item] = res_data[item]
            _response = str_data
        else:
            _response = data
        return _response


class Login(BaseAPIView):
    def post(self, request, request_data, *args, **kwargs):
        data, status = self.auth.login(request, request_data)
        return data, status


class Logout(BaseAPIView):
    @permissions(IsAuthenticated)
    def get(self, request, request_data):
        data, status = self.auth.logout(request, request_data)
        return data, status
