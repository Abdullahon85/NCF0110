"""Test runner that swaps the file-based caches for per-process in-memory ones,
so tests never share throttle counters or cached pages with each other's runs
or with a development server on the same machine."""
from django.conf import settings
from django.test.runner import DiscoverRunner


class IsolatedCacheTestRunner(DiscoverRunner):
    def setup_test_environment(self, **kwargs):
        super().setup_test_environment(**kwargs)
        settings.CACHES = {
            alias: {"BACKEND": "django.core.cache.backends.locmem.LocMemCache", "LOCATION": f"test-{alias}"}
            for alias in settings.CACHES
        }
