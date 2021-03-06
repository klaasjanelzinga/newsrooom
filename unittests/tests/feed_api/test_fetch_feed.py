import pytest
from faker import Faker

from api.feed_api import get_all_feeds, subscribe_to_feed
from core_lib.application_data import Repositories
from core_lib.repositories import User, Feed
from tests.conftest import feed_factory


@pytest.mark.asyncio
async def test_fetch_user(repositories: Repositories, faker: Faker, feed: Feed, user: User, user_bearer_token):
    # Subscribe user to 1 feed and create another (not subscribed)
    await subscribe_to_feed(feed_id=feed.feed_id.__str__(), authorization=user_bearer_token)
    await repositories.feed_repository.upsert(feed_factory(faker))
    response = await get_all_feeds(authorization=user_bearer_token)

    assert len(response) == 2
    subscribed_feed = [response_feed for response_feed in response if response_feed.feed.feed_id == feed.feed_id][0]
    assert subscribed_feed.user_is_subscribed
    not_subscribed_feed = [response_feed for response_feed in response if response_feed.feed.feed_id != feed.feed_id][0]
    assert not not_subscribed_feed.user_is_subscribed
