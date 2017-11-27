import json

from django.http import HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from .decorators import permissions
from .permission import IsAuthenticated
from .status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN
from .exceptions import (
    RequestStructureException,
    ResponseError,
    ResponseBadRequestMsgList,
    ResponseOkMessage,
    ResponseFailMessage,
)

from .fields import JSONField
from .settings import rester_settings

response_structure = rester_settings['RESPONSE_STRUCTURE']


class BaseAPIView(View):
    auth = rester_settings['AUTH_BACKEND']()
    request_fields = {}

    @classmethod
    def as_view(cls, **kwargs):
        view = super(BaseAPIView, cls).as_view()
        view.cls = cls
        return csrf_exempt(view)

    @property
    def _common_request_structure(self):
        # check if request_fields are common to any http method or not
        common_structure = False
        for key in self.request_fields.keys():
            if key in self._allowed_methods():
                common_structure = True
                break
        return common_structure

    @staticmethod
    def _set_response(_response):
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
        return HttpResponse(pure_response, content_type=content_type, status=status)

    def _request_data_validate(self, method, request_data):
        if self.request_fields == {}:
            return request_data, []

        if self._common_request_structure:
            request_structure = self.request_fields.get(method, None)
        else:
            request_structure = self.request_fields

        if not request_structure:
            raise RequestStructureException(
                'request data structure is not valid, check for documentation or leave blank')

        request_data, messages = self._check_json_field(request_data, request_structure)
        return request_data, messages

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
        request_data = dict()
        method = request.method
        if method in self._allowed_methods():
            if method == 'GET':
                request_data = json.loads(json.dumps(request.GET)) if request.GET else {}
            elif method in ('POST', 'PUT', 'PATCH',):
                request_data = json.loads(request.body.decode('utf-8')) if request.body else {}
        return request_data

    def dispatch(self, request, *args, **kwargs):
        request_data = self._set_request_data(request)
        if not isinstance(request_data, (dict, list)):
            return self._set_response((['Request data is not json serializable'], HTTP_400_BAD_REQUEST))
        # auth = self.auth_class(request, request_data)
        user, messages = self.auth.authenticate(request)
        if not messages and user:
            request.user = user
        request_data, messages_ = self._request_data_validate(request.method, request_data)
        messages += messages_
        if messages:
            return self._set_response((messages, HTTP_403_FORBIDDEN))
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed

        _response = self.try_response(handler, request, request_data, *args, **kwargs)
        return self._set_response(_response)

    @staticmethod
    def try_response(handler, request, request_data, *args, **kwargs):
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
        if response_structure:
            res_data = {'success': success,
                        'message': message,
                        'data': data,
                        }
            str_data = dict(response_structure)
            for item in str_data.keys():
                if str_data[item] in res_data:
                    str_data[item] = res_data[item]
            content = (str_data, response_status)
        else:
            content = data, response_status

        return content


class Login(BaseAPIView):
    def post(self, request, request_data, *args, **kwargs):
        data, status = self.auth.login(request, request_data)
        return data, status


class Logout(BaseAPIView):
    @permissions(IsAuthenticated)
    def get(self, request, request_data):
        data, status = self.auth.logout(request, request_data)
        return data, status
