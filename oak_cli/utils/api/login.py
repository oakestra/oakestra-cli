import oak_cli.utils.api.custom_requests as custom_requests
from oak_cli.utils.api.common import SYSTEM_MANAGER_URL
from oak_cli.utils.api.custom_http import HttpMethod
from oak_cli.utils.exceptions.types import OakCLIExceptionTypes

_login_token = ""


class LoginFailed(Exception):
    pass


def _login_and_set_token() -> str:
    response = custom_requests.CustomRequest(
        custom_requests.RequestCore(
            http_method=HttpMethod.POST,
            base_url=SYSTEM_MANAGER_URL,
            api_endpoint="/api/auth/login",
            data={"username": "Admin", "password": "Admin"},
            custom_headers={"accept": "application/json", "Content-Type": "application/json"},
        ),
        custom_requests.RequestAuxiliaries(
            what_should_happen="Login",
            oak_cli_exception_type=OakCLIExceptionTypes.LOGIN,
        ),
    ).execute()

    global _login_token
    _login_token = response["token"]
    return _login_token


def get_login_token() -> str:
    if _login_token == "":
        return _login_and_set_token()
    return _login_token
