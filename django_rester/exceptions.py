from .status import (
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_200_OK,
)


class ResterException(Exception):
    pass


class ResponseError(ResterException):
    response_status = HTTP_500_INTERNAL_SERVER_ERROR


class ResponseBadRequest(ResponseError):
    response_status = HTTP_400_BAD_REQUEST


class ResponseServerError(ResponseError):
    response_status = HTTP_500_INTERNAL_SERVER_ERROR


class ResponseAuthError(ResponseError):
    response_status = HTTP_401_UNAUTHORIZED


class ResponseOkMessage(ResponseError):
    def __init__(self, message='', data=None, status=HTTP_200_OK):
        self.message = message
        self.data = data
        self.response_status = status


class ResponseFailMessage(ResponseError):
    def __init__(self, message='', data=None, status=HTTP_500_INTERNAL_SERVER_ERROR):
        self.message = message
        self.data = data
        self.response_status = status


class ResponseBadRequestMsgList(ResponseError):
    def __init__(self, messages=None, status=HTTP_400_BAD_REQUEST):
        self.response_status = status
        if messages and isinstance(messages, (list, tuple)):
            self.messages = list(messages)
        elif isinstance(messages, str):
            self.messages = [messages]
        else:
            self.messages = []


class JSONFieldError(ResterException):
    # base JSONField exception
    pass


class JSONFieldModelTypeError(JSONFieldError):
    # JSONField exception, raises when type of model parameter is not valid
    pass


class JSONFieldModelError(JSONFieldError):
    # JSONField exception, raises when value of model parameter is not valid
    pass


class JSONFieldTypeError(JSONFieldError):
    # JSONField exception, simple TypeError inside JSONField class
    pass


class JSONFieldValueError(JSONFieldError):
    # JSONField exception, simple ValueError inside JSONField class
    pass


class BaseAPIViewException(Exception):
    # BaseAPIView exception class
    pass


class RequestStructureException(BaseAPIViewException):
    # raise if request structure is invalid
    pass


class ResponseStructureException(RequestStructureException):
    # raise if response structure is invalid
    pass
