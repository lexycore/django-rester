import datetime
import jwt
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django_rediser import RedisStorage
from ..status import HTTP_200_OK, HTTP_401_UNAUTHORIZED
from .settings import rester_jwt_settings
from django_rester.exceptions import ResponseAuthError

redis_db = None
if isinstance(rester_jwt_settings['USE_REDIS'], int) and not isinstance(rester_jwt_settings['USE_REDIS'], bool):
    redis_db = rester_jwt_settings['USE_REDIS']


class BaseAuth:
    _key = '_token'
    _rs = RedisStorage(db=redis_db)
    settings = rester_jwt_settings

    @classmethod
    def _set_payload(cls, user):
        exp = datetime.datetime.timestamp(
            datetime.datetime.now() + datetime.timedelta(seconds=cls.settings['EXPIRE']))
        payload = {item: getattr(user, item, None) for item in cls.settings['PAYLOAD_LIST'] if
                   hasattr(user, item)}
        payload.update({"exp": exp})
        return payload

    def _push_token(self, token):
        self._rs.sadd(self._key, token)

    def _rem_token(self, token):
        return self._rs.srem(self._key, token)

    def _is_member(self, token):
        return self._rs.sismember(self._key, token)

    @classmethod
    def _get_token(cls, request):
        token, messages = None, []
        token = str(request.META.get(cls.settings['AUTH_HEADER'], ''))
        if token:
            if cls.settings['AUTH_HEADER_PREFIX'] and token.startswith(
                    cls.settings['AUTH_HEADER_PREFIX']):
                token = token[len(cls.settings['AUTH_HEADER_PREFIX']):].lstrip()
            else:
                messages.append('Wrong token prefix')
        return token, messages

    @staticmethod
    def _get_user(**kwargs):
        user_model = get_user_model()
        user = user_model.objects.get(**kwargs)
        return user

    def _get_user_data(self, token):
        is_member, data, exp_date, user_data, user, messages = True, None, None, {}, None, []
        if self.settings['USE_REDIS']:
            is_member = self._is_member(token)
        if is_member:
            try:
                data = jwt.decode(token, self.settings['SECRET'], algorithms=[self.settings['ALGORITHM']])
            except jwt.DecodeError:
                messages.append('Wrong authentication token')
            except jwt.ExpiredSignatureError:
                messages.append('Authentication token expired')

            if data:
                exp_date = data.pop('exp', None)
                user_data = {item: data.get(item, None) for item in self.settings['PAYLOAD_LIST']}
            if exp_date and user_data and exp_date > datetime.datetime.now().timestamp():
                user = self._get_user(**user_data)
        else:
            messages.append('Authentication token is not valid or expired')

        return user, messages


class Auth(BaseAuth):
    def login(self, request, request_data):
        token = None
        login = request_data.get(self.settings['LOGIN_FIELD'], None)
        password = request_data.get('password', '')
        if login is not None:
            user = authenticate(username=login, password=password)
        else:
            user = None
        if user:
            payload = self._set_payload(user)
            token, status = jwt.encode(payload, self.settings['SECRET'],
                                       algorithm=self.settings['ALGORITHM']).decode('utf-8'), HTTP_200_OK
            encoded = {'token': token}
        else:
            raise ResponseAuthError('Authentication failed')
        if status == HTTP_200_OK and self.settings['USE_REDIS'] and token:
            self._push_token(token)
        return encoded, status

    def logout(self, request, request_data):
        token, messages = self._get_token(request)
        result = None
        if self.settings['USE_REDIS']:
            result = self._rem_token(token)
        if result == 0:
            messages.append('Token not found')
        elif not result:
            messages.append('Simple logout')
        else:
            messages.append('Token logout')

        return messages, HTTP_200_OK

    def authenticate(self, request_data):
        user, messages = None, None
        token, messages = self._get_token(request_data)
        if token:
            user, messages = self._get_user_data(token)
        if messages:
            user = None
        return user, messages

    def register(self, request_data):
        pass
