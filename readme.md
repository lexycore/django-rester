### Package for creating API with built-in validation and authentication

This product is designed to build API endpoints of varying complexity and nesting.

The core is a view class - BaseApiView (the inheritor of the standard django view)

***
##### 1. settings

DEFAULT settings (may be overrided):
```python
DJANGO_RESTER = {
    'RESTER_JWT': {
        'JWT_SECRET': 'secret_key',
        'JWT_EXPIRATION_DELTA': timedelta(seconds=60 * 60 * 24 * 14),
        'JWT_AUTH_HEADER': 'Authorization',
        'JWT_AUTH_HEADER_PREFIX': 'JWT',
        'JWT_ALGORITHM': 'HS256',
        'JWT_PAYLOAD_LIST': ['email'],
        'JWT_USE_REDIS': False,
        },
    'RESTER_LOGIN_FIELD': 'username',
    'RESTER_AUTH_BACKEND': 'django_rester.jwt'
    'RESTER_TRY_RESPONSE_STRUCTURE': False,
}
```

**JWT** - JWT authentication settings (in case of 'RESTER_AUTH_BACKEND' = 'django_rester.jwt')*:

&nbsp;&nbsp;&nbsp;&nbsp; **JWT_SECRET** - JWT secret key

&nbsp;&nbsp;&nbsp;&nbsp; **JWT_EXPIRATION_DELTA** - token expiration time (datetime.now() + RESTER_EXPIRATION_DELTA)

&nbsp;&nbsp;&nbsp;&nbsp; **JWT_AUTH_HEADER** - HTTP headed, which will be used for auth token.

&nbsp;&nbsp;&nbsp;&nbsp; **JWT_AUTH_HEADER_PREFIX** - prefix for auth token ("Authorization:\<prefix> \<token>")

&nbsp;&nbsp;&nbsp;&nbsp; **JWT_ALGORITHM** - cypher alghorithm

&nbsp;&nbsp;&nbsp;&nbsp; **JWT_PAYLOAD_LIST** - payload list for token encode (will take specified **user** attributes to create token)

&nbsp;&nbsp;&nbsp;&nbsp; **JWT_USE_REDIS** - use redis-server to store tokens or not

**RESTER_LOGIN_FIELD** - user login field (default is 'username' as in django)

**RESTER_AUTH_BACKEND** - authentication backend*

**RESTER_TRY_RESPONSE_STRUCTURE** - use or not @try_response() decorator by default.
***

##### 2. built-in statuses

```from django_rester.status import ...```
<br><br><br>
status.py from [DRF](http://www.django-rest-framework.org/), it's simple and easy to understand.

Any statuses used in this documentation are described in that file.
***
##### 3. built-in exceptions:


```from django_rester.exceptions import ...```
<br><br><br>
you may use those exceptions to interact with **@try_response** decorator (good example of usage), or in any other way you want

**class ResponseError(Exception)**

&nbsp;&nbsp;&nbsp;&nbsp;base exception class, standard Exception inheritor, added response status - HTTP_500_INTERNAL_SERVER_ERROR

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
***
##### 4. permisson classes

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
##### 5. built-in decorators

```from django_rester.decorators import ...```
<br><br><br>
**@try_response(structure=True)**

May be used to handle custom built-in exceptions and return structured data:

&nbsp;&nbsp;&nbsp;&nbsp;**{"success": bool, "message": list, "data": dict}**

to response handler.

if **structure=False** then exeptions will be handled, but clean data and status will be returned
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

##### 6. built-in views

```from django_rester.views import ...```
<br><br><br>
**class BaseApiView(View)**

inherits from standard django view.

class attributes:

&nbsp;&nbsp;&nbsp;&nbsp;**auth_class** - authentication class of current authentication backend

&nbsp;&nbsp;&nbsp;&nbsp;**request_fields** - request validator

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
```
from django_rester.views import BaseAPIView
from django_rester.decorators import try_response, permissions
from django_rester.exceptions import ResponseOkMessage
from django_rester.permission import IsAdmin
from django_rester.status import HTTP_200_OK
from app.models import Model
from django_rester.fields import JSONField

class TestView(BaseAPIView):

    request_fields = {"POST": {
        "id": JSONField(field_type=int, required=True, ),
        "title": JSONField(field_type=str, required=True, default='some_title'),
        "fk": [{"id": JSONField(field_type=int, required=True)}],
    }}


    def retrieve_items():
        return Model.objects.all()

    def create_item(title):
        item, cre = Model.objects.get_or_create(title=title)
        return item, cre

    @try_response
    @permissions(AllowAny)
    def get(self, request, request_data, *args, **kwargs):
        items = self.retrieve_items()
        response_data = {...here we should build some response structure...}***
        return response_data, HTTP_200_OK

    @try_response
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
```
from django.conf.urls import url
from .views import TestView

urlpatterns = [
    url(r'^test/', TestView.as_view()),
]
```
***

##### 7. built-in fields

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

methods:

&nbsp;&nbsp;&nbsp;&nbsp;**validate** - validate field value with parameters
***

*- Right now only one authentication backend is available - JWT

**- BaseApiView is on active development stage, other attributes and methods will be added soon

***- automatic response structure build - one of the nearest tasks