import difflib
import re
from datetime import datetime, timedelta
from typing import List, Optional
from urllib.parse import urlparse

import pytz

from core_lib.application_data import repositories
from core_lib.date_utils import now_in_utc
from core_lib.repositories import Feed, FeedItem, User, NewsItem, RefreshResult


def are_titles_similar(title_1: str, title_2: str) -> bool:
    title_1 = re.sub(r"\[.*]", "", title_1)
    title_2 = re.sub(r"\[.*]", "", title_2)
    return len(title_1) > 10 and difflib.SequenceMatcher(None, title_1, title_2).ratio() > 0.516


def item_is_still_relevant(item: FeedItem) -> bool:
    try:
        return item.created_on > (datetime.now(tz=pytz.utc) - timedelta(hours=18))
    except TypeError:
        return item.created_on > (datetime.now() - timedelta(hours=18))


def upsert_new_feed_items_for_feed(feed: Feed, feed_items: List[FeedItem]) -> int:
    current_feed_item_links = [
        feed_item.link for feed_item in repositories.feed_item_repository.fetch_all_for_feed(feed)
    ]
    new_feed_items = [
        new_feed_item for new_feed_item in feed_items if new_feed_item.link not in current_feed_item_links
    ]
    repositories.feed_item_repository.upsert_many(new_feed_items)
    return len(new_feed_items)


def upsert_new_items_for_feed(feed: Feed, updated_feed: Feed, feed_items_from_rss: List[FeedItem]) -> int:
    """
    Upload new items as feed item and news item for users.

    - Upload all the feed-items if feed item did not exist yet.
    - If feed-item exists, tick the last_seen timestamp.
    - For all subscribed users, make news items and upsert new feed items.
    - Set number_of_items, last_fetched and mutable details for the feed itself.

    returns: Number of new NewsItems created.
    """
    current_feed_items = repositories.feed_item_repository.fetch_all_for_feed(feed)
    subscribed_users = repositories.user_repository.fetch_subscribed_to(feed)

    updated_feed_items: List[FeedItem] = []  # updated feed_items that will be updated.
    new_feed_items: List[FeedItem] = []  # new feed_items that will be inserted.
    new_news_items: List[NewsItem] = []  # news items that will be inserted.
    updated_news_items: List[NewsItem] = []  # news items that are updated.

    for user in subscribed_users:
        current_news_items = repositories.news_item_repository.fetch_all_non_read_for_feed(feed, user)
        for new_feed_item in feed_items_from_rss:
            feed_items_with_same_link = [item for item in current_feed_items if item.link == new_feed_item.link]
            if len(feed_items_with_same_link) > 0:  # We have seen this item already, update last seen.
                for feed_item in feed_items_with_same_link:
                    feed_item.last_seen = now_in_utc()
                updated_feed_items.extend(feed_items_with_same_link)
            else:
                # New feed item.
                new_feed_items.append(new_feed_item)
                current_feed_items.append(new_feed_item)

                # Check if there is already a similar news item to flag alternates.
                news_items_similar_titles = [
                    news_item
                    for news_item in current_news_items
                    if are_titles_similar(title_1=news_item.title, title_2=new_feed_item.title)
                ]
                # If no similar news items, just insert new news item and feed item, else update existing news item.
                if len(news_items_similar_titles) == 0:
                    new_news_item = news_item_from_feed_item(new_feed_item, feed, user)
                    new_news_items.append(new_news_item)
                    current_news_items.append(new_news_item)
                else:
                    for existing_news_item in news_items_similar_titles:
                        existing_news_item.append_alternate(
                            new_feed_item.link, new_feed_item.title, determine_favicon_link(new_feed_item, feed)
                        )
                        existing_news_item.published = new_feed_item.published or now_in_utc()
                        updated_news_items.append(existing_news_item)

    # Upsert the new and updated feed_items.
    repositories.feed_item_repository.upsert_many(new_feed_items)
    repositories.feed_item_repository.upsert_many(updated_feed_items)
    repositories.news_item_repository.upsert_many(new_news_items)
    repositories.news_item_repository.upsert_many(updated_news_items)

    # Update information in feed item with latest information from the url.
    feed.last_fetched = datetime.utcnow()
    feed.description = updated_feed.description
    feed.title = updated_feed.title
    feed.number_of_items = feed.number_of_items + len(new_feed_items)
    repositories.feed_repository.upsert(feed)
    return len(new_news_items)


def update_users_unread_count_with_refresh_results(refresh_results: List[Optional[RefreshResult]]) -> None:
    """
    Update the count of unread items per feed per subscribed user.
    """
    for refresh_result in [result for result in refresh_results if result is not None]:
        subscribed_users = repositories.user_repository.fetch_subscribed_to(refresh_result.feed)
        for user in subscribed_users:
            user.number_of_unread_items += refresh_result.number_of_items
        repositories.user_repository.upsert_many(subscribed_users)


def news_items_from_feed_items(feed_items: List[FeedItem], feed: Feed, user: User) -> List[NewsItem]:
    return [news_item_from_feed_item(feed_item, feed, user) for feed_item in feed_items]


domain_to_favicon_map = {
    "www.sikkom.nl": "https://www.sikkom.nl/wp-content/themes/sikkom-v3/img/favicon.ico",
    "www.gic.nl": "https://www.gic.nl/img/favicon.ico",
    "www.rtvnoord.nl": "https://www.rtvnoord.nl/Content/Images/noord/favicon.ico",
    "www.filtergroningen.nl": "https://i1.wp.com/www.filtergroningen.nl/wp-content/uploads/2017/03/favicon.png?fit=32%2C32&#038;ssl=1",
    "www.tivolivredenburg.nl": "https://www.tivolivredenburg.nl/wp-content/themes/tivolivredenburg/favicon.ico",
    "www.vera-groningen.nl": "https://www.vera-groningen.nl/vera/assets/img/favicon.png",
    "https://www.desmaakvanstad.nl": "https://www.desmaakvanstad.nl/wp-content/uploads/2017/08/cropped-FAVICON-1.jpg",
}


def determine_favicon_link(feed_item: FeedItem, feed: Feed) -> str:
    feed_item_link_domain = urlparse(feed_item.link).netloc
    feed_domain = urlparse(feed.url).netloc
    if feed_item_link_domain == feed_domain:
        return feed.image_url or f"https://{feed_domain}/favicon.ico"
    return domain_to_favicon_map.get(feed_item_link_domain, f"https://{feed_item_link_domain}/favicon.ico")


def news_item_from_feed_item(feed_item: FeedItem, feed: Feed, user: User) -> NewsItem:
    return NewsItem(
        feed_id=feed_item.feed_id,
        user_id=user.user_id,
        feed_item_id=feed_item.feed_item_id,
        feed_title=feed.title,
        title=feed_item.title,
        description=feed_item.description,
        link=feed_item.link,
        published=feed_item.published or now_in_utc(),
        favicon=determine_favicon_link(feed_item, feed),
        created_on=now_in_utc(),
    )
