import os

import requests

from oak_cli.utils.types import CustomEnum

SYSTEM_MANAGER_URL = f"http://{os.environ.get('SYSTEM_MANAGER_URL')}:10000"


class HttpMethod(CustomEnum):
    GET = "get"
    POST = "post"
    PUT = "put"
    PATCH = "patch"
    DELETE = "delete"

    def call(cls, **kwargs) -> requests.Response:
        method_map = {
            cls.GET: requests.get,
            cls.POST: requests.post,
            cls.PUT: requests.put,
            cls.PATCH: requests.patch,
            cls.DELETE: requests.delete,
        }
        method = method_map.get(cls)

        if method:
            return method(**kwargs)
        else:
            raise ValueError(f"Unsupported HTTP method: {cls.value}")
