"""JWT helpers: staff-only login and refresh-token revocation."""
from rest_framework import exceptions
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken


class StaffTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Issues tokens to staff only. Non-staff get the same 401 as a wrong
    password, so the response does not reveal that the account exists."""

    def validate(self, attrs):
        data = super().validate(attrs)
        if not self.user.is_staff:
            raise exceptions.AuthenticationFailed(
                self.error_messages["no_active_account"], "no_active_account"
            )
        return data


def revoke_all_refresh_tokens(user) -> int:
    """Blacklist every refresh token issued to the user; returns how many were newly revoked."""
    revoked = 0
    for token in OutstandingToken.objects.filter(user=user):
        _, created = BlacklistedToken.objects.get_or_create(token=token)
        revoked += int(created)
    return revoked
