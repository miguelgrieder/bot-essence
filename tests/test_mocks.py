import httpx
import pytest
import requests


def test_env() -> None:
    from bot_essence.config import get_settings

    settings = get_settings()

    assert settings.app_env == "TEST"


def test_req() -> None:
    with pytest.raises(RuntimeError, match="disabled"):
        requests.get("http://localhost", timeout=1)


@pytest.mark.asyncio
async def test_async_httpx() -> None:
    with pytest.raises(RuntimeError, match="disabled"):
        async with httpx.AsyncClient() as client:
            await client.get("http://localhost", timeout=1)
