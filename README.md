Django-Rester
=============

[![build](https://travis-ci.org/lexycore/django-rester.svg?branch=master)](https://travis-ci.org/lexycore/django-rester)
[![codacy](https://api.codacy.com/project/badge/Grade/dee291831b0b43158e2d2301726e2c00)](https://www.codacy.com/app/lexycore/django-rester/dashboard)
[![pypi](https://img.shields.io/pypi/v/django-rester.svg)](https://pypi.python.org/pypi/django-rester)
[![license](https://img.shields.io/pypi/l/django-rester.svg)](https://github.com/lexycore/django-rester/blob/master/LICENSE)

### Package for creating API with built-in validation and authentication

This product is designed to build API endpoints of varying complexity and nesting.

The core is a view class - BaseApiView (the inheritor of the standard django view)

***
##### 1. requirements

1. Python 3+

2. Django 1.11+

***
##### 2. settings

DEFAULT settings (may be overridden):
```python
DJANGO_RESTER = {
    'AUTH_BACKEND': 'django_rester.rester_jwt', 
    'RESPONSE_STRUCTURE': False,
    'CORS_ACCESS': False,
    'FIELDS_CHECK_EXCLUDED_METHODS': ['OPTIONS', 'HEAD'],
    'SOFT_RESPONSE_VALIDATION': False, 
}

DJANGO_RESTER_JWT: {
    'SECRET': 'secret_key',
    'EXPIRE': 60 * 60 * 24 * 14,  # seconds
    'AUTH_HEADER': 'Authorization',
    'AUTH_HEADER_PREFIX': 'jwt',
    'ALGORITHM': 'HS256',
    'PAYLOAD_LIST': ['username'],
    'USE_REDIS': False,  # here can be an int value (redis db number)
    'LOGIN_FIELD': 'username', # as default django login field
}
```

**DJANGO_RESTER** - django-rester settings:

&nbsp;&nbsp;&nbsp;&nbsp; **AUTH_BACKEND** - authentication backend*

&nbsp;&nbsp;&nbsp;&nbsp; **RESPONSE_STRUCTURE** - False or can be a dict with 'success', 'message' and 'data' as a values

&nbsp;&nbsp;&nbsp;&nbsp; **CORS_ACCESS** - CORS control, True, False, "*", hosts_string

&nbsp;&nbsp;&nbsp;&nbsp; **FIELDS_CHECK_EXCLUDED_METHODS** - methods, which will not be processed with body structure checks 

&nbsp;&nbsp;&nbsp;&nbsp; **SOFT_RESPONSE_VALIDATION** - if True, response will not be cut off if it will contain additional to response_structure fields 

**DJANGO_RESTER_JWT** - JWT authentication settings (in case of 'RESTER_AUTH_BACKEND' = 'django_rester.rester_jwt')*:

&nbsp;&nbsp;&nbsp;&nbsp; **SECRET** - JWT secret key

&nbsp;&nbsp;&nbsp;&nbsp; **EXPIRE** - token expiration time (datetime.now() + RESTER_EXPIRATION_DELTA)

&nbsp;&nbsp;&nbsp;&nbsp; **AUTH_HEADER** - HTTP headed, which will be used for auth token.

&nbsp;&nbsp;&nbsp;&nbsp; **AUTH_HEADER_PREFIX** - prefix for auth token ("Authorization:\<prefix> \<token>")

&nbsp;&nbsp;&nbsp;&nbsp; **ALGORITHM** - cypher algorithm

&nbsp;&nbsp;&nbsp;&nbsp; **PAYLOAD_LIST** - payload list for token encode (will take specified **user** attributes to create token)

&nbsp;&nbsp;&nbsp;&nbsp; **USE_REDIS** - use redis-server to store tokens or not

&nbsp;&nbsp;&nbsp;&nbsp; **LOGIN_FIELD** - user login field (default is 'username' as in django)
***

##### 3. built-in statuses

```from django_rester.status import ...```
<br><br><br>
slightly modified status.py from [DRF](http://www.django-rest-framework.org/), it's simple and easy to understand.

Any statuses used in this documentation are described in that file.
***
##### 4. built-in exceptions:


```from django_rester.exceptions import ...```
<br><br><br>
Exceptions, which will help you to recognise errors related to django-rester

**class ResterException(Exception)**

&nbsp;&nbsp;&nbsp;&nbsp;base django-rester exception, standard Exception inheritor

**class ResponseError(Exception)**

&nbsp;&nbsp;&nbsp;&nbsp;ResponseError inheritor, added response status - HTTP_500_INTERNAL_SERVER_ERROR

**class ResponseBadRequest(ResponseError)**

&nbsp;&nbsp;&nbsp;&nbsp;ResponseError inheritor, response status changed to HTTP_400_BAD_REQUEST

**class ResponseServerError(ResponseError)**

&nbsp;&nbsp;&nbsp;&nbsp;ResponseError inheritor

**class ResponseAuthError(ResponseError)**

&nbsp;&nbsp;&nbsp;&nbsp;ResponseError inheritor, response status changed to HTTP_401_UNAUTHORIZED

**class ResponseOkMessage(ResponseError)**

&nbsp;&nbsp;&nbsp;&nbsp;ResponseError inheritor

&nbsp;&nbsp;&nbsp;&nbsp;acceptable arguments: *, message='', data=None, status=HTTP_200_OK

**class ResponseFailMessage(ResponseError)**

&nbsp;&nbsp;&nbsp;&nbsp;ResponseError inheritor

&nbsp;&nbsp;&nbsp;&nbsp;acceptable arguments: *, message='', data=None, status=HTTP_500_INTERNAL_SERVER_ERROR

**class ResponseBadRequestMsgList(ResponseError)**

&nbsp;&nbsp;&nbsp;&nbsp;ResponseError inheritor

&nbsp;&nbsp;&nbsp;&nbsp;acceptable arguments: *, messages=None, status=HTTP_400_BAD_REQUEST

&nbsp;&nbsp;&nbsp;&nbsp;messages could be list, tuple or string.

**class JSONFieldError(ResterException)**

&nbsp;&nbsp;&nbsp;&nbsp;ResterException inheritor, base JSONField exception

**class JSONFieldModelTypeError(JSONFieldError)**

&nbsp;&nbsp;&nbsp;&nbsp;JSONField exception, raises when type of model parameter is not valid

**class JSONFieldModelError(JSONFieldError)**

&nbsp;&nbsp;&nbsp;&nbsp;JSONField exception, raises when value of model parameter is not valid

**class JSONFieldTypeError(JSONFieldError)**

&nbsp;&nbsp;&nbsp;&nbsp;JSONField exception, simple TypeError inside JSONField class

**class JSONFieldValueError(JSONFieldError)**

&nbsp;&nbsp;&nbsp;&nbsp;JSONField exception, simple ValueError inside JSONField class

**class BaseAPIViewException(Exception)**

&nbsp;&nbsp;&nbsp;&nbsp;BaseAPIView exception class

**class RequestStructureException(BaseAPIViewException)**

&nbsp;&nbsp;&nbsp;&nbsp;raise if request structure is invalid

**class ResponseStructureException(RequestStructureException)**

&nbsp;&nbsp;&nbsp;&nbsp;raise if response structure is invalid
***
##### 5. permission classes

```from django_rester.permission import ...```
<br><br><br>
Permission classes created to interact wih **@permissions()** decorator (good example of usage), or in any other way you want

All permission classes accepts only one argument on **init** - django view **request** object.

All permission classes has 2 attributes, defined on **init**:

**check**: Bool - returns **True** or **False** if request.user may or may not access endpoint method

**message**: could be a string or list of messages
<br><br><br>
**class BasePermission**

&nbsp;&nbsp;&nbsp;&nbsp;contains all base permission methods, it is not recommended to use it directly in projects

**class IsAuthenticated(BasePermission)**

&nbsp;&nbsp;&nbsp;&nbsp;check = **True** if user authenticated and active, else **False**

**class IsAdmin(BasePermission)**

&nbsp;&nbsp;&nbsp;&nbsp;check = **True** if user authenticated and active and is_superuser, else **False**

**class AllowAny(BasePermission)**

&nbsp;&nbsp;&nbsp;&nbsp;check = **True** for any user (even anonymous)

***
##### 6. built-in decorators

```from django_rester.decorators import ...```
<br><br><br>
**@permissions()**

&nbsp;&nbsp;&nbsp;&nbsp;accepts permission class or list, tuple of classes.

&nbsp;&nbsp;&nbsp;&nbsp;if check is passed, then user will be allowed to use endpoint

example:
```
class Example(BaseApiView):

    @permissions(IsAdmin)
    def post(request, request_data, *args, **kwargs):
        pass
```
***

##### 7. built-in views

```from django_rester.views import ...```
<br><br><br>
**class BaseApiView(View)**

inherits from standard django view.

class attributes:

&nbsp;&nbsp;&nbsp;&nbsp;**auth** - authentication backend instance

&nbsp;&nbsp;&nbsp;&nbsp;**request_fields** - request validator (use JSONField to build this validator)

&nbsp;&nbsp;&nbsp;&nbsp;**response_fields** - response validator (use JSONField to build this validator)

<br>

class HTTP methods (get, post, put, etc...) accepts next arguments: request, request_data, *args, **kwargs

&nbsp;&nbsp;&nbsp;&nbsp;**request** - standard django view request object

&nbsp;&nbsp;&nbsp;&nbsp;**request_data** - all received request parameters as json serialized object

User authentication with selected authentication backend
<br><br><br>
**class Login(BaseApiView)**

Could be used to authenticate user with selected authentication backend.

&nbsp;&nbsp;&nbsp;&nbsp;Allowed method is 'POST' only.

&nbsp;&nbsp;&nbsp;&nbsp;Requires username and password in request parameters (username fieldname parameter may be set in settings)

&nbsp;&nbsp;&nbsp;&nbsp;Returns token and HTTP_200_OK status code if authentication success, error message and HTTP_401_UNAUTHORIZED if failed
<br><br><br>
**class Logout(BaseApiView)**

Could be used to logout (with redis support) or just to let know frontend about logout process.
<br><br><br>
Any view could be used the same way, here is a **simple example**:

&nbsp;&nbsp;&nbsp;&nbsp;**app/views.py:**
```python
from django_rester.views import BaseAPIView
from django_rester.decorators import permissions
from django_rester.exceptions import ResponseOkMessage
from django_rester.permission import IsAdmin
from django_rester.status import HTTP_200_OK
from app.models import Model # import Model from your application
from django_rester.fields import JSONField

class TestView(BaseAPIView):

    request_fields = {"POST": {
        "id": JSONField(field_type=int, required=True, ),
        "title": JSONField(field_type=str, required=True, default='some_title'),
        "fk": [{"id": JSONField(field_type=int, required=True)}],
    }}

    response_fields = {"POST": {
        "id": JSONField(field_type=int, required=True, ),
        "title": JSONField(field_type=str, required=True, default='some_title'),
        # ...
    }}
    
    def retrieve_items():
        return Model.objects.all()

    def create_item(title):
        item, cre = Model.objects.get_or_create(title=title)
        return item, cre

    @permissions(AllowAny)
    def get(self, request, request_data, *args, **kwargs):
        items = self.retrieve_items()
        response_data = {...here we should build some response structure...}***
        return response_data, HTTP_200_OK

    @permissions(IsAdmin)
    def post(self, request, request_data, *args, **kwargs):
        title = request_data.get('title', None)
        # no need to check 'if title', because it is allready validated by 'available_fields'
        # ... here we will do some view magic with the rest request_data
        item, cre = self.create_item(title)
        if not cre:
            raise ResponseOkMessage(message='Item allready exists', data={'title': title})
        response_data = {...here we should build some response structure...}***

        return response_data
```

&nbsp;&nbsp;&nbsp;&nbsp;**app/urls.py:**
```python
from django.conf.urls import url
from .views import TestView

urlpatterns = [
    url(r'^test/', TestView.as_view()),
]
```
***

##### 8. built-in fields

```from django_rester.fields import ...```
<br><br><br>
**class JSONField**

class attributes:

&nbsp;&nbsp;&nbsp;&nbsp;**field_type** - data type (int, float, str, bool)

&nbsp;&nbsp;&nbsp;&nbsp;**required** - field is required

&nbsp;&nbsp;&nbsp;&nbsp;**default** - default value if not specified

&nbsp;&nbsp;&nbsp;&nbsp;**blank** - may or may not be blank

&nbsp;&nbsp;&nbsp;&nbsp;**model** - model for foreign relations

&nbsp;&nbsp;&nbsp;&nbsp;**field** - field for foreign relations

methods (public), with normal usage, you won't need them in your code:

&nbsp;&nbsp;&nbsp;&nbsp;**check_type** - validate type of JSONField value

&nbsp;&nbsp;&nbsp;&nbsp;**validate** - validate field value with parameters
***

*- There is only one authentication backend available for now - RESTER_JWT

**- BaseApiView is on active development stage, other attributes and methods could be added soon

***- automatic response structure build - one of the nearest tasks