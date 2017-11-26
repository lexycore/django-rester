from .permission import BasePermission
from .exceptions import (
    ResponseError,
    ResponseBadRequestMsgList,
    ResponseOkMessage,
    ResponseFailMessage,
)
from .status import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_200_OK, HTTP_401_UNAUTHORIZED
from django.conf import settings

DJANGO_RESTER = settings.DJANGO_RESTER
use_structure = DJANGO_RESTER['RESTER_TRY_RESPONSE_STRUCTURE']

def try_response(structure=use_structure):
    def try_response_decorator(f):
        def wrapper(view, request, request_data, *args, **kwargs):
            message = []
            success = None
            data = None
            try:
                success = True
                data = f(view, request, request_data, *args, **kwargs)
                response_status = HTTP_200_OK
                if type(data) == tuple and len(data) == 2:
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
            if structure:
                content = ({'success': success,
                            'message': message,
                            'data': data,
                            }, response_status)
            else:
                content = data, response_status

            return content

        return wrapper

    return try_response_decorator


def permissions(*perms):
    def permissions_decorator(f):
        def wrapper(view, request, request_data, *args, **kwargs):
            checked, message = True, ''
            for perm_item in perms:
                if issubclass(perm_item, BasePermission):
                    auth_check = perm_item(request)
                    checked, message = auth_check.check, auth_check.message
                    if not checked:
                        break
            if checked:
                data = f(view, request, request_data, *args, **kwargs)
            else:
                data = message, HTTP_401_UNAUTHORIZED
            return data

        return wrapper

    return permissions_decorator
