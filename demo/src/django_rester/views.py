import json

from django.http import HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from .decorators import try_response, permissions
from .permission import IsAuthenticated
from .status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN
from django.conf import settings
from .exceptions import RequestStructureException
from .fields import JSONField

rester_settings = getattr(settings, 'DJANGO_RESTER', None)
auth_backend = rester_settings.get('RESTER_AUTH_BACKEND', None)


class BaseAPIView(View):
    auth_class = auth_backend.Auth
    request_fields = {}

    # @staticmethod
    # def data_tuple_list(request_data):
    #     request_data = request_data if isinstance(request_data, (list, tuple)) else []
    #     return request_data if request_data != [] else False
    #
    # @staticmethod
    # def data_dict(request_data):
    #     request_data = request_data if isinstance(request_data, (dict)) else {}
    #     return request_data

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

    # @staticmethod
    # def validate(self, request_data: (list, dict), available_fields: list = None, required_fields: list = None):
    def _request_data_validate(self, method, request_data):

        # def check_available(_item, fields):
        #     _fields_ok = True
        #     for key in _item.keys():
        #         if key not in fields:
        #             _fields_ok = False
        #     return _fields_ok
        #
        # def check_required(_item, fields):
        #     _fields_ok = True
        #     for field in fields:
        #         if field not in _item.keys():
        #             _fields_ok = False
        #     return _fields_ok
        #
        # def check_inner(_item):
        #     _fields_ok = False
        #     if required_fields and (len(_item) < len(required_fields)):
        #         return False
        #     if available_fields and request_data:
        #         _fields_ok = check_available(_item, available_fields)
        #     if required_fields and request_data and _fields_ok:
        #         _fields_ok = check_required(_item, required_fields)
        #     return _fields_ok
        #
        # fields_ok = False
        # if type(request_data) == list:
        #     for item in request_data:
        #         fields_ok = check_inner(item)
        #
        # if type(request_data) == dict:
        #     fields_ok = check_inner(request_data)
        #
        # if not required_fields and not available_fields:
        #     fields_ok = True

        # common request structure for all http methods or not
        # common_structure = self._common_request_structure
        # messages = []

        if self.request_fields == {}:
            return request_data, None

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
                # TODO maybe add some other checks
        return request_data

    def dispatch(self, request, *args, **kwargs):
        request_data = self._set_request_data(request)
        if not isinstance(request_data, (dict, list)):
            return self._set_response((['Request data is not json serializable'], HTTP_400_BAD_REQUEST))
        self.auth = self.auth_class(request, request_data)
        user, messages = self.auth.authenticate()
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

        _response = handler(request, request_data, *args, **kwargs)
        return self._set_response(_response)


class Login(BaseAPIView):
    @try_response()
    def post(self, request, request_data, *args, **kwargs):
        data, status = self.auth.login()
        return data, status


class Logout(BaseAPIView):
    @try_response()
    @permissions(IsAuthenticated)
    def get(self, request, request_data):
        data, status = self.auth.logout()
        return data, status
