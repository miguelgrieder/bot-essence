import logging
from enum import Enum
from functools import lru_cache
from typing import Any, Literal, Union

from pydantic import PositiveInt, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings


class OperationModes(Enum):
    local = "local"
    distributed = "distributed"


class Settings(BaseSettings):
    # - APP -
    app_host: str = "0.0.0.0"  # noqa: S104
    app_port: int = 8000
    app_title: str = __package__.title().replace("_", " ")
    app_workers: PositiveInt = 1
    app_operation_mode: Union[OperationModes, Literal["auto"]] = "auto"

    # - Env Control -
    app_env: str = "DEV"
    # app_accepted_envs: list[str] = ["*"]

    # - Rate Limiter -
    rate_limiter_enabled: bool = True

    # - Authentication -
    auth_middleware_enabled: bool = True
    auth_middleware_secret: SecretStr = SecretStr("")

    # - MongoDB Config -
    mongo_variables_host: str = "localhost"
    mongo_variables_port: int = 27017
    mongo_variables_username: str
    mongo_variables_password: str

    # - CORS -
    # cors_origins: list[str] = ["*"]

    # - Logging (Local) -
    log_level: Union[int, str] = "INFO"

    # - Development -
    dev_uvicorn_reload: bool = False

    # - Waha -
    waha_url: str
    waha_token: str
    waha_self_id: str = ""

    class Config:
        env_file = ".env"

    @field_validator("log_level", mode="before")
    @classmethod
    def valid_log_level(cls, v: Union[int, str], info: Any) -> Union[int, str]:
        if isinstance(v, str):
            v = v.upper()
            if not isinstance(logging.getLevelName(v), int):
                error_msg = "O `log_level` passado é inválido"
                raise ValueError(error_msg)  # noqa: TRY004
        return v

    @model_validator(mode="after")  # type: ignore[arg-type]
    @classmethod
    def auto_app_op_mode(cls, values: "Settings") -> "Settings":
        if values.app_operation_mode != "auto":
            return values

        workers: int = values.app_workers

        # Add here other settings that can indicate the used OperationModes
        if workers > 1:
            values.app_operation_mode = OperationModes.distributed
        else:
            values.app_operation_mode = OperationModes.local
        return values

    @model_validator(mode="after")  # type: ignore[arg-type]
    @classmethod
    def assert_distributed_if_multiple_workers(cls, values: "Settings") -> "Settings":
        workers: int = values.app_workers
        operation_mode: Union[OperationModes, Literal["auto"]] = values.app_operation_mode
        if workers > 1 and operation_mode != OperationModes.distributed:
            error_msg = "Operation mode `distributed` is required for multiple workers"
            raise ValueError(error_msg)
        return values


@lru_cache(1)
def get_settings() -> Settings:
    return Settings()
