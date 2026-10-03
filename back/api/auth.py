"""JWT helpers: staff-only token issuance/refresh and refresh-token revocation."""
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.utils import get_md5_hash_password
from django.utils import timezone
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken


def staff_user_authentication_rule(user) -> bool:
    """SIMPLE_JWT['USER_AUTHENTICATION_RULE']: SimpleJWT applies it on login and
    on every refresh, before any token is created. Non-staff get the same 401 as
    a wrong password, and a user who loses staff status cannot refresh anymore."""
    return user is not None and user.is_active and user.is_staff


def revoke_all_refresh_tokens(user) -> int:
    """Blacklist the user's live refresh tokens (unexpired, not yet revoked) in two
    queries; returns how many were newly revoked."""
    live = OutstandingToken.objects.filter(
        user=user, expires_at__gt=timezone.now(), blacklistedtoken__isnull=True
    )
    tokens = list(live)
    BlacklistedToken.objects.bulk_create(
        [BlacklistedToken(token=t) for t in tokens], ignore_conflicts=True
    )
    return len(tokens)


class PasswordAwareTokenRefreshSerializer(TokenRefreshSerializer):
    """With CHECK_REVOKE_TOKEN, SimpleJWT rejects access tokens issued before a password
    change, but still refreshes the old refresh token into such dead access tokens.
    Refuse the refresh instead, so the admin panel goes back to the login page."""

    def validate(self, attrs):
        refresh = RefreshToken(attrs["refresh"])
        user_id = refresh.payload.get(api_settings.USER_ID_CLAIM)
        user = get_user_model().objects.filter(**{api_settings.USER_ID_FIELD: user_id}).first()
        claim = refresh.payload.get(api_settings.REVOKE_TOKEN_CLAIM)
        if user is None or claim != get_md5_hash_password(user.password):
            raise AuthenticationFailed("The password has changed; please log in again.", "password_changed")
        return super().validate(attrs)
