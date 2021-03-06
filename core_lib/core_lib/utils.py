from base64 import b64encode
from datetime import datetime
from typing import Optional

import pytz


def now_in_utc() -> datetime:
    return datetime.now(tz=pytz.utc)


def bytes_to_str_base64(bytes_to_decode: bytes) -> str:
    return b64encode(bytes_to_decode).decode("utf-8")


def sanitize_link(link: str) -> str:
    return link.replace("\n", "").strip()


def parse_description(description: Optional[str]) -> Optional[str]:
    if description is None:
        return None
    if len(description) > 1400:
        description = description[0:1400]
    return description
