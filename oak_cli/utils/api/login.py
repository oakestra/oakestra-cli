import oak_cli.utils.api as oak_api

_login_token = ""


class LoginFailed(Exception):
    pass


def _login_and_set_token() -> str:
    data = {"username": "Admin", "password": "Admin"}
    headers = {"accept": "application/json", "Content-Type": "application/json"}

    json_data = oak_api.main.handle_request(
        base_url=oak_api.common.SYSTEM_MANAGER_URL,
        http_method=oak_api.common.HttpMethod.POST,
        api_endpoint="/api/auth/login",
        headers=headers,
        data=data,
        what_should_happen="Login",
    )

    global _login_token
    _login_token = json_data["token"]
    return _login_token


def get_login_token() -> str:
    if _login_token == "":
        return _login_and_set_token()
    return _login_token
