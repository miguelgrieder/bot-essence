import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import bot_essence
from bot_essence import api, config
from bot_essence.lifespan import lifespan

log = logging.getLogger(__name__)

settings = config.get_settings()


swagger_ui_parameters = {
    "displayRequestDuration": True,
    "filter": True,
    "syntaxHighlight.theme": "arta",
}

app = FastAPI(
    title=settings.app_title,
    description="",
    version=bot_essence.__version__,
    swagger_ui_parameters=swagger_ui_parameters,
    lifespan=lifespan,
)

# app.state.limiter = get_limiter()
# app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


@app.get("/health_check")
def health_check() -> dict[str, str]:
    return {"ping": "pong"}


# @app.get("/env_test")
# def env_test(token: str):
#     return settings.model_dump()

log.debug("Adding api router to the app")
app.include_router(api.router)
