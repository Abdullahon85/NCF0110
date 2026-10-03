"""JWT helpers: staff-only token issuance/refresh and refresh-token revocation."""
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken


def staff_user_authentication_rule(user) -> bool:
    """SIMPLE_JWT['USER_AUTHENTICATION_RULE']: SimpleJWT applies it on login and
    on every refresh, before any token is created. Non-staff get the same 401 as
    a wrong password, and a user who loses staff status cannot refresh anymore."""
    return user is not None and user.is_active and user.is_staff


def revoke_all_refresh_tokens(user) -> int:
    """Blacklist every refresh token issued to the user; returns how many were newly revoked."""
    revoked = 0
    for token in OutstandingToken.objects.filter(user=user):
        _, created = BlacklistedToken.objects.get_or_create(token=token)
        revoked += int(created)
    return revoked
