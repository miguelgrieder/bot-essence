import json
from typing import Any, Optional

import requests


class MockedResponse:
    def __init__(
        self,
        *,
        url: str,
        status_code: int,
        request_name: str = "",
        json_data: Any = None,
        raises: Optional[Exception] = None,
    ) -> None:
        self.url = url
        self.status_code = status_code
        self._json_data = json_data
        self._request_name = request_name
        if raises:
            raise raises

    def json(self, **kwargs: Any) -> Any:
        return self._json_data

    @property
    def text(self) -> str:
        return json.dumps(self._json_data)

    @property
    def reason(self) -> str:
        return f"HTTP Error - {self._request_name}"

    @property
    def content(self) -> bytes:
        return self.text.encode()

    def raise_for_status(self) -> None:
        http_error_msg = ""
        if 400 <= self.status_code < 500:
            http_error_msg = f"{self.status_code} Client Error: {self.reason} for url: {self.url}"

        elif 500 <= self.status_code < 600:
            http_error_msg = f"{self.status_code} Server Error: {self.reason} for url: {self.url}"
        if http_error_msg:
            raise requests.HTTPError(
                http_error_msg,
                response=self,  # type: ignore
            )
