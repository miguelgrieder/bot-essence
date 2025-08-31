import logging

from fastapi import APIRouter, Request

log = logging.getLogger(__name__)

router = APIRouter()


@router.post("/")
def filter_activities(request: Request) -> None:
    return None
