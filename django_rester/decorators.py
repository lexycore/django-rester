from .permission import BasePermission
from .status import HTTP_401_UNAUTHORIZED


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
