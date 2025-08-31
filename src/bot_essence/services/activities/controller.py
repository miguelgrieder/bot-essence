import logging
from typing import Any

from pymongo import MongoClient
from pymongo.collection import Collection

from bot_essence import config

settings = config.get_settings()
log = logging.getLogger(__name__)

# Setup MongoDB connection
client: MongoClient[Any] = MongoClient(
    f"mongodb://{settings.mongo_variables_username}:"
    f"{settings.mongo_variables_password}@"
    f"{settings.mongo_variables_host}:"
    f"{settings.mongo_variables_port}/"
)
db = client["bot-essence"]
activity_collection: Collection[dict[str, Any]] = db["data"]
