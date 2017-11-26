from django_rester.views import BaseAPIView
from django_rester.decorators import try_response, permissions
from django_rester.exceptions import ResponseOkMessage
from django_rester.permission import IsAuthenticated, IsAdmin, AllowAny
from django.conf import settings
from django_rester.fields import JSONField


class TestView(BaseAPIView):
    # available_fields = ['a','b','c']
    # required_fields = ['a']

    request_fields = {"POST": {
        "id": JSONField(field_type=int, required=True, ),
        "title": JSONField(field_type=str, required=True, default='some_title'),
        "fk": [{"id": JSONField(field_type=int, required=True)}],
    }}

    @try_response()
    @permissions(AllowAny)
    def get(self, request, request_data):
        a = request.user
        b = settings.DJANGO_RESTER
        response_data = request_data
        return response_data

    @try_response()
    @permissions(IsAdmin)
    def post(self, request, request_data):
        response_data = request_data
        if not response_data:
            raise ResponseOkMessage(message='Example OK message', data={'example': 'data'})
        # a = 1
        # messages = ['a is not allowed']
        # if a:
        #    raise ResponseBadRequestMsgList(messages=messages)
        return response_data
