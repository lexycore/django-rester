from django_rester.status import HTTP_200_OK
from django_rester.views import BaseAPIView
from django_rester import fields


class TestView(BaseAPIView):
    request_fields = {
        "POST": {
            "id": fields.Int(required=True),
            "title": fields.String(required=False, default='some_title'),
        },
        "GET": {
            "id": fields.Int(required=False, default=0),
            "title": fields.String(required=False, default='some_title'),
        }
    }

    response_fields = {
        "POST": {
            "id": fields.Int(required=True),
            "title": fields.String(required=True, default='some_title'),
            "fk": [{"id": fields.Int(required=True)}]
        },
        "GET": {
            "id": fields.Int(required=False),
            "title": fields.String(required=True, default='some_title'),
        }
    }

    def get(self, request, *args, **kwargs):
        return self.request_data, HTTP_200_OK

    def post(self, request, *args, **kwargs):
        response = dict(self.request_data)
        response.update({
            "id": "1",
            "jk": 'kj',
            "title": "kljkhjkj",
            "lkjljl": 657,
            "fk": [{"id": 233, "asd": 222}]
        })
        return response, HTTP_200_OK
