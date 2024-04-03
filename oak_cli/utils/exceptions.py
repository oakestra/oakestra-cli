from http import HTTPStatus


class OakCliException(Exception):
    def __init__(
        self,
        msg: str,
        http_status: HTTPStatus = None,
    ):
        self.msg = msg
        self.http_status = http_status


class OakestraException(OakCliException):
    pass


class MQTTException(OakCliException):
    pass


class LoginException(OakCliException):
    pass
