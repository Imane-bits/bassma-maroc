from django.core.cache import cache


def is_rate_limited(request, key, limit=5, window_seconds=600):
    ip = request.META.get("REMOTE_ADDR", "unknown")
    cache_key = f"ratelimit:{key}:{ip}"
    count = cache.get(cache_key, 0)
    if count >= limit:
        return True
    cache.set(cache_key, count + 1, window_seconds)
    return False
