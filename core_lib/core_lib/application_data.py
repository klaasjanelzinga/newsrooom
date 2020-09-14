import logging
import os
from unittest.mock import Mock, MagicMock

from google.cloud import datastore
from google.cloud.datastore import Client

from core_lib.repositories import (
    FeedRepository,
    SubscriptionRepository,
    FeedItemRepository,
    NewsItemRepository,
    UserRepository,
)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__file__)


def not_in_unit_tests() -> bool:
    return "unit_tests" not in os.environ


DATASTORE_CLIENT = datastore.Client() if not_in_unit_tests() else MagicMock(Client)

user_repository: UserRepository = UserRepository(DATASTORE_CLIENT) if not_in_unit_tests() else MagicMock(UserRepository)
feed_repository: FeedRepository = FeedRepository(DATASTORE_CLIENT) if not_in_unit_tests() else MagicMock(FeedRepository)
feed_item_repository: FeedItemRepository = (
    FeedItemRepository(DATASTORE_CLIENT) if not_in_unit_tests() else MagicMock(FeedItemRepository)
)
subscription_repository: SubscriptionRepository = (
    SubscriptionRepository(DATASTORE_CLIENT) if not_in_unit_tests() else MagicMock(SubscriptionRepository)
)
news_item_repository: NewsItemRepository = (
    NewsItemRepository(DATASTORE_CLIENT) if not_in_unit_tests() else MagicMock(NewsItemRepository)
)
