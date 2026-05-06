import time
from typing import Annotated

from fastapi import Depends

from app.core.config import Settings, get_settings
from app.core.exceptions import RateLimitError
from app.core.redis import RedisClient


async def _workspace_rate_limit(
    slug: str,
    redis: RedisClient,
    settings: Settings = Depends(get_settings),
) -> None:
    """Enforce a fixed-window rate limit scoped to a workspace.

    Uses the workspace slug (already present as a path parameter) as the
    bucket key — no extra DB lookup required.

    Args:
        slug: Workspace slug from the URL path.
        redis: Async Redis client.
        settings: Application settings (limit + window size).

    Raises:
        RateLimitError: When the workspace exceeds the configured request limit.
    """
    bucket = int(time.time()) // settings.rate_limit_window_seconds
    key = f"rl:{slug}:{bucket}"

    count = await redis.incr(key)
    if count == 1:
        await redis.expire(key, settings.rate_limit_window_seconds)

    if count > settings.rate_limit_requests:
        raise RateLimitError()


WorkspaceRateLimit = Annotated[None, Depends(_workspace_rate_limit)]
