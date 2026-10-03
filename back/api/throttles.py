# api/throttles.py
from django.conf import settings
from django.core.cache import caches
from rest_framework.throttling import AnonRateThrottle


class LoginRateThrottle(AnonRateThrottle):
    """
    Rate limiting for login attempts to prevent brute force attacks.
    Maximum 5 login attempts per hour per real client IP.
    """
    scope = 'login'
    rate = '5/hour'
    # Dedicated cache: page caching in 'default' cannot evict these counters.
    cache = caches['throttle']

    def get_ident(self, request):
        # Take the address appended by the nearest trusted proxy (the right end of
        # X-Forwarded-For); anything to the left of it is supplied by the client.
        num_proxies = settings.TRUSTED_PROXY_COUNT
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        if num_proxies <= 0 or not xff:
            return request.META.get('REMOTE_ADDR')
        addrs = [a.strip() for a in xff.split(',')]
        return addrs[-min(num_proxies, len(addrs))]
