from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase

from config.env import (
    LEAKED_SECRET_KEYS,
    env_bool,
    env_list,
    resolve_secret_key,
)


class EnvHelpersTest(SimpleTestCase):
    def test_env_bool_parses_variants(self):
        self.assertTrue(env_bool("X", False, {"X": "TRUE"}))
        self.assertFalse(env_bool("X", True, {"X": "off"}))
        self.assertTrue(env_bool("X", True, {}))

    def test_env_bool_rejects_garbage(self):
        with self.assertRaises(ImproperlyConfigured):
            env_bool("X", False, {"X": "maybe"})

    def test_env_list_strips_and_drops_empty(self):
        self.assertEqual(env_list("H", [], {"H": " a.com, ,b.com,"}), ["a.com", "b.com"])

    def test_env_list_default_is_copied(self):
        default = ["a"]
        result = env_list("H", default, {})
        result.append("b")
        self.assertEqual(default, ["a"])

    def test_secret_key_required_in_production(self):
        with self.assertRaises(ImproperlyConfigured):
            resolve_secret_key({}, debug=False)

    def test_dev_fallback_key_is_random_not_committed(self):
        # A fallback committed to the repo would be forgeable like the leaked key.
        first = resolve_secret_key({}, debug=True)
        second = resolve_secret_key({}, debug=True)
        self.assertNotEqual(first, second)
        self.assertGreaterEqual(len(first), 50)

    def test_dev_fallback_refused_on_render(self):
        # Render sets RENDER=true; a Render deploy must never run without its own key.
        with self.assertRaises(ImproperlyConfigured):
            resolve_secret_key({"RENDER": "true"}, debug=True)

    def test_leaked_key_rejected_even_in_debug(self):
        leaked = next(iter(LEAKED_SECRET_KEYS))
        for debug in (True, False):
            with self.assertRaises(ImproperlyConfigured):
                resolve_secret_key({"SECRET_KEY": leaked}, debug=debug)

    def test_insecure_prefix_rejected_in_production(self):
        with self.assertRaises(ImproperlyConfigured):
            resolve_secret_key({"SECRET_KEY": "django-insecure-" + "a" * 50}, debug=False)

    def test_short_key_rejected_in_production(self):
        with self.assertRaises(ImproperlyConfigured):
            resolve_secret_key({"SECRET_KEY": "x" * 49}, debug=False)

    def test_valid_key_returned(self):
        key = "k" * 50
        self.assertEqual(resolve_secret_key({"SECRET_KEY": key}, debug=False), key)
