# api/throttles.py
from django.conf import settings
from django.core.cache import caches
from rest_framework.permissions import SAFE_METHODS
from rest_framework.throttling import AnonRateThrottle, SimpleRateThrottle, UserRateThrottle


class RealClientIPMixin:
    """Identify the client by the address appended by the nearest trusted proxy
    (right end of X-Forwarded-For); anything to the left is client-supplied."""

    def get_ident(self, request):
        num_proxies = settings.TRUSTED_PROXY_COUNT
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        if num_proxies <= 0 or not xff:
            return request.META.get('REMOTE_ADDR')
        addrs = [a.strip() for a in xff.split(',')]
        return addrs[-min(num_proxies, len(addrs))]


class LoginRateThrottle(RealClientIPMixin, AnonRateThrottle):
    """
    Rate limiting for login attempts to prevent brute force attacks.
    Maximum 5 login attempts per hour per real client IP.
    """
    scope = 'login'
    rate = '5/hour'
    # Dedicated cache: page caching in 'default' cannot evict these counters.
    cache = caches['throttle']


PUBLIC_WRITE_RATE = '30/hour'


class PublicWriteThrottle(RealClientIPMixin, SimpleRateThrottle):
    """One shared budget per real client IP for public POSTs: reviews,
    questions and contact messages. Reads and staff are never limited by it."""
    scope = 'public_write'
    rate = PUBLIC_WRITE_RATE
    cache = caches['throttle']

    def allow_request(self, request, view):
        # Reads are free; staff managing orders/reviews through the same
        # endpoints must not burn the public budget.
        if request.method in SAFE_METHODS or getattr(request.user, 'is_staff', False):
            return True
        return super().allow_request(request, view)

    def get_cache_key(self, request, view):
        return self.cache_format % {'scope': self.scope, 'ident': self.get_ident(request)}


ORDER_RATE = '20/hour'


class PublicOrderThrottle(PublicWriteThrottle):
    """Checkout has its own budget so review/contact spam from a shared
    (e.g. carrier NAT) IP cannot block customers from placing orders."""
    scope = 'public_order'
    rate = ORDER_RATE


# Keep the project-wide anon/user limits and add the dedicated budget.
PUBLIC_WRITE_THROTTLES = [AnonRateThrottle, UserRateThrottle, PublicWriteThrottle]
ORDER_THROTTLES = [AnonRateThrottle, UserRateThrottle, PublicOrderThrottle]
