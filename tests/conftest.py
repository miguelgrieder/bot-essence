from typing import Any

import pytest
from dotenv import load_dotenv
from pytest_mock import MockerFixture

load_dotenv("./tests/.env.test", override=True)


def pytest_configure(config: pytest.Config) -> None:
    from bot_essence import config as ms_config

    settings = ms_config.get_settings()

    if settings.app_env != "TEST":
        reason = "Failed to load test environment config"
        pytest.exit(reason)


@pytest.fixture(autouse=True)
def avoid_request_communication(mocker: MockerFixture) -> None:
    def fail(*args: Any, **kwargs: Any) -> None:
        msg = "Communication disabled for tests"
        raise RuntimeError(msg)

    async def async_fail(*args: Any, **kwargs: Any) -> None:
        msg = "Communication disabled for tests"
        raise RuntimeError(msg)

    mocker.patch("requests.Session.send", new=fail)
    mocker.patch("httpx.AsyncClient.send", new=async_fail)
    # Synchronous `httpx` ("httpx.Client.send") is used by the `TestClient`.
    # To allow this usage and because `requests` is used for
    # synchronous requests throughout the code (and not `httpx`), it will not be mocked.
