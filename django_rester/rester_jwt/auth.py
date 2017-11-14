import datetime

import jwt
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model

from django_rediser.rediser import RedisStorage
from ..status import HTTP_200_OK, HTTP_401_UNAUTHORIZED


class BaseAuth:
    _key = '_token'
    _header_prefix = 'http_'

    def __init__(self, request, request_data: (list, dict), *args, **kwargs):
        self._rs = RedisStorage()
        self.request = request
        self.request_data = request_data

        self._settings = getattr(settings, 'DJANGO_RESTER')
        self._username_field = self._settings.get('RESTER_LOGIN_FIELD')
        self._jwt_settings = self._settings.get('RESTER_JWT')
        self._jwt_use_redis = self._jwt_settings.get('JWT_USE_REDIS')
        self._jwt_header = self._jwt_settings.get('JWT_AUTH_HEADER')
        self._jwt_payload_list = self._jwt_settings.get('JWT_PAYLOAD_LIST')
        self._jwt_token_prefix = self._jwt_settings.get('JWT_AUTH_HEADER_PREFIX')
        self._jwt_secret = self._jwt_settings.get('JWT_SECRET')
        self._jwt_algorithm = self._jwt_settings.get('JWT_ALGORITHM')
        self._jwt_expiration_delta = self._jwt_settings.get('JWT_EXPIRATION_DELTA')

    def _set_payload(self, user) -> dict:
        exp = datetime.datetime.timestamp(
            datetime.datetime.now() + self._jwt_expiration_delta)
        payload = {item: getattr(user, item, None) for item in self._jwt_payload_list if getattr(user, item, None) is not None}
        payload.update({"exp": exp})
        return payload

    def _push_token(self, token: str):
        self._rs.sadd(self._key, token)

    def _rem_token(self, token: str) -> int:
        return self._rs.srem(self._key, token)

    def _is_member(self, token: str) -> bool:
        return self._rs.sismember(self._key, token)

    def _get_token(self):
        token, messages, token_split = None, [], None
        token_string = self.request.META.get('{}{}'.format(self._header_prefix, self._jwt_header).upper(), None)
        if token_string:
            token_split = token_string.split()
        if token_split and self._jwt_token_prefix == token_split[0]:
            token = token_split[1]
        elif token_split and self._jwt_token_prefix != token_split[0]:
            messages.append('Wrong token prefix')

        return token, messages

    def _get_user(self, **kwargs):
        UserModel = get_user_model()
        user = UserModel.objects.get(**kwargs)
        return user

    def _get_user_data(self, token):
        is_member, data, exp_date, user_data, user, messages = True, None, None, {}, None, []
        if self._jwt_use_redis:
            is_member = self._is_member(token)
        if is_member:
            try:
                data = jwt.decode(token, self._jwt_secret, algorithms=[self._jwt_algorithm])
            except jwt.DecodeError:
                messages.append('Wrong authentication token')

            if data:
                exp_date = data.pop('exp', None)
                user_data = {item: data.get(item, None) for item in self._jwt_payload_list}
            if exp_date and user_data and datetime.datetime.fromtimestamp(exp_date) > datetime.datetime.now():
                user = self._get_user(**user_data)
            else:
                messages.append('Authentication token is expired')
        else:
            messages.append('Authentication token is not valid or expired')

        return user, messages


class Auth(BaseAuth):
    def login(self):
        token = None
        login = self.request_data.get(self._settings.get('RESTER_LOGIN_FIELD'))
        password = self.request_data.get('password', None)
        user = authenticate(username=login, password=password)
        payload = self._set_payload(user)
        if user:
            token, status = jwt.encode(payload, self._jwt_secret, algorithm=self._jwt_algorithm).decode(
                'utf-8'), HTTP_200_OK
            encoded = {'token': token}
        else:
            encoded, status = ['Authentication failed'], HTTP_401_UNAUTHORIZED
        if status == HTTP_200_OK and self._jwt_use_redis and token:
            self._push_token(token)
        return encoded, status

    def logout(self):
        token, messages = self._get_token()
        result = None
        if self._jwt_use_redis:
            result = self._rem_token(token)
        if result == 0:
            messages.append('Token not found')
        elif not result:
            messages.append('Simple logout')
        else:
            messages.append('Token logout')

        return messages, HTTP_200_OK

    def authenticate(self):
        user, messages = None, None
        token, messages = self._get_token()
        if token:
            user, messages = self._get_user_data(token)
        if messages:
            user = None
        return user, messages