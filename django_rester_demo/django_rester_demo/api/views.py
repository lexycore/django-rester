from django_rester.status import HTTP_200_OK
from django_rester.views import BaseAPIView
from django_rester.fields import JSONField


class TestView(BaseAPIView):
    request_fields = {"POST": {
        "id": JSONField(field_type=int, required=True, ),
        "title": JSONField(field_type=str, required=True, default='some_title'),
        #"fk": [{"id": JSONField(field_type=int, required=True)}]}
    },
        "GET": {"title": JSONField(field_type=str, required=True, default='some_title'),
                }
    }

    response_fields = {"POST": {
        "id": JSONField(field_type=int, required=True, ),
        "title": JSONField(field_type=str, required=True, default='some_title'),
        #"fk": [{"id": JSONField(field_type=int, required=True)}]}
    },
        "GET": {"title": JSONField(field_type=str, required=True, default='some_title'),
                }
    }

    def get(self, request, request_data, *args, **kwargs):
        return request_data, HTTP_200_OK

    def post(self, request, request_data, *args, **kwargs):
        response = {"id":1, "jk":'kj', "title":"kljkhjkj", "lkjljl":657,"fk":[{"id5":233}]}
        return response, HTTP_200_OK
