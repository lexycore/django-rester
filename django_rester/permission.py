class BasePermission:
    def __init__(self, request):
        self.check, self.message = False, ''
        self.request = request

    @staticmethod
    def _get_message(check, messages):
        return messages.get('SUCCESS' if check else 'FAIL', None)

    def _is_authenticated(self):
        check = self.request.user.is_authenticated and not self.request.user.is_anonymous and self.request.user.is_active
        messages = {'SUCCESS': ['Auth OK'], 'FAIL': ['Required credentials are not provided']}
        message = self._get_message(check, messages)
        return check, message

    def _is_admin(self):
        check = self.request.user.is_superuser and self.request.user.is_active
        messages = {'SUCCESS': ['Auth OK'], 'FAIL': ['Required credentials are not provided or user is not superuser']}
        message = self._get_message(check, messages)
        return check, message

    def _allow_any(self):
        check = True
        messages = {'SUCCESS': ['Auth OK']}
        message = self._get_message(check, messages)
        return check, message


class IsAuthenticated(BasePermission):
    def __init__(self, request):
        super().__init__(request)
        self.check, self.message = self._is_authenticated()


class IsAdmin(BasePermission):
    def __init__(self, request):
        super().__init__(request)
        self.check, self.message = self._is_admin()


class AllowAny(BasePermission):
    def __init__(self, request):
        super().__init__(request)
        self.check, self.message = self._allow_any()
