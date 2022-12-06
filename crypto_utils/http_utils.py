import typing

import requests

from crypto_utils import exceptions


def request(
    url: str, headers: dict[str, str] = {"H": "Content-Type: application/json"}
) -> typing.Any:
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        return resp.json()
    raise exceptions.RequestError(status_code=resp.status_code)
