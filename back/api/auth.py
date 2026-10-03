"""JWT helpers: staff-only token issuance/refresh and refresh-token revocation."""
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
