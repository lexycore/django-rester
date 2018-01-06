import datetime
import jwt
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django_rediser import RedisStorage
from ..status import HTTP_200_OK, HTTP_401_UNAUTHORIZED
from .settings import rester_jwt_settings

redis_db = None
if isinstance(rester_jwt_settings['USE_REDIS'], int) and not isinstance(rester_jwt_settings['USE_REDIS'], bool):
    redis_db = rester_jwt_settings['USE_REDIS']


class BaseAuth:
    _key = '_token'
    _rs = RedisStorage(db=redis_db)

    @staticmethod
    def _set_payload(user):
        exp = datetime.datetime.timestamp(
            datetime.datetime.now() + datetime.timedelta(seconds=rester_jwt_settings['EXPIRE']))
        payload = {item: getattr(user, item, None) for item in rester_jwt_settings['PAYLOAD_LIST'] if
                   hasattr(user, item)}
        payload.update({"exp": exp})
        return payload

    def _push_token(self, token):
        self._rs.sadd(self._key, token)

    def _rem_token(self, token):
        return self._rs.srem(self._key, token)

    def _is_member(self, token):
        return self._rs.sismember(self._key, token)

    @staticmethod
    def _get_token(request):
        token, messages = None, []
        token = str(request.META.get(rester_jwt_settings['AUTH_HEADER'], ''))
        if token:
            if rester_jwt_settings['AUTH_HEADER_PREFIX'] and token.startswith(
                    rester_jwt_settings['AUTH_HEADER_PREFIX']):
                token = token[len(rester_jwt_settings['AUTH_HEADER_PREFIX']):].lstrip()
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
        if rester_jwt_settings['USE_REDIS']:
            is_member = self._is_member(token)
        if is_member:
            try:
                data = jwt.decode(token, rester_jwt_settings['SECRET'], algorithms=[rester_jwt_settings['ALGORITHM']])
            except jwt.DecodeError:
                messages.append('Wrong authentication token')
            except jwt.ExpiredSignatureError:
                messages.append('Authentication token expired')

            if data:
                exp_date = data.pop('exp', None)
                user_data = {item: data.get(item, None) for item in rester_jwt_settings['PAYLOAD_LIST']}
            if exp_date and user_data and exp_date > datetime.datetime.now().timestamp():
                user = self._get_user(**user_data)
        else:
            messages.append('Authentication token is not valid or expired')

        return user, messages


class Auth(BaseAuth):
    def login(self, request, request_data):
        token = None
        login = request_data.get(rester_jwt_settings['LOGIN_FIELD'], None)
        password = request_data.get('password', '')
        if login is not None:
            user = authenticate(username=login, password=password)
        else:
            user = None
        if user:
            payload = self._set_payload(user)
            token, status = jwt.encode(payload, rester_jwt_settings['SECRET'],
                                       algorithm=rester_jwt_settings['ALGORITHM']).decode('utf-8'), HTTP_200_OK
            encoded = {'token': token}
        else:
            encoded, status = ['Authentication failed'], HTTP_401_UNAUTHORIZED
        if status == HTTP_200_OK and rester_jwt_settings['USE_REDIS'] and token:
            self._push_token(token)
        return encoded, status

    def logout(self, request, request_data):
        token, messages = self._get_token(request)
        result = None
        if rester_jwt_settings['USE_REDIS']:
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
