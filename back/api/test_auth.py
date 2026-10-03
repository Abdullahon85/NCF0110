"""JWT hardening: staff-only tokens, logout and password change revoke refresh tokens (audit items 6-7)."""
from django.contrib.auth.models import User
from django.core.cache import caches
from django.test import TestCase
from rest_framework.test import APIClient

PASSWORD = "Str0ng-pass-123"
NEW_PASSWORD = "N3w-strong-pass-456"


class AuthHardeningTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create_user("admin", password=PASSWORD, is_staff=True)
        User.objects.create_user("user", password=PASSWORD)

    def setUp(self):
        for c in caches.all(initialized_only=False):
            c.clear()

    def _login(self, username):
        return APIClient().post("/api/admin/auth/login/", {"username": username, "password": PASSWORD}, format="json")

    def _refresh(self, token):
        return APIClient().post("/api/admin/auth/refresh/", {"refresh": token}, format="json")

    def _change_password(self, access, old, new):
        api = APIClient()
        api.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        return api.post("/api/admin/auth/change-password/", {"old_password": old, "new_password": new}, format="json")

    def test_non_staff_cannot_get_tokens(self):
        self.assertEqual(self._login("user").status_code, 401)

    def test_staff_gets_tokens(self):
        self.assertIn("refresh", self._login("admin").data)

    def test_logout_revokes_refresh(self):
        t = self._login("admin").data
        api = APIClient()
        api.credentials(HTTP_AUTHORIZATION=f"Bearer {t['access']}")
        self.assertEqual(api.post("/api/admin/auth/logout/", {"refresh": t["refresh"]}, format="json").status_code, 200)
        self.assertEqual(self._refresh(t["refresh"]).status_code, 401)

    def test_logout_without_access_token_still_revokes(self):
        t = self._login("admin").data
        self.assertEqual(APIClient().post("/api/admin/auth/logout/", {"refresh": t["refresh"]}, format="json").status_code, 200)
        self.assertEqual(self._refresh(t["refresh"]).status_code, 401)

    def test_logout_requires_refresh_field(self):
        self.assertEqual(APIClient().post("/api/admin/auth/logout/", {}, format="json").status_code, 400)

    def test_change_password_revokes_other_sessions(self):
        old = self._login("admin").data
        current = self._login("admin").data
        self.assertEqual(self._change_password(current["access"], PASSWORD, NEW_PASSWORD).status_code, 200)
        self.assertEqual(self._refresh(old["refresh"]).status_code, 401)

    def test_change_password_returns_working_new_tokens(self):
        t = self._login("admin").data
        r = self._change_password(t["access"], PASSWORD, NEW_PASSWORD)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self._refresh(r.data["refresh"]).status_code, 200)

    def test_refresh_rotates_and_revokes_previous(self):
        # Contract the admin frontend relies on: store data.refresh after every refresh.
        t = self._login("admin").data
        r = self._refresh(t["refresh"])
        self.assertEqual(r.status_code, 200)
        self.assertIn("refresh", r.data)
        self.assertEqual(self._refresh(t["refresh"]).status_code, 401)
