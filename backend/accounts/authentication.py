from django.contrib.auth import get_user_model
from rest_framework import authentication, exceptions

from accounts.jwt import decode_token

User = get_user_model()


class JWTAuthentication(authentication.BaseAuthentication):
    keyword = "Bearer"

    def authenticate(self, request):
        header = authentication.get_authorization_header(request).decode("utf-8")
        if not header:
            return None

        parts = header.split()
        if len(parts) != 2 or parts[0] != self.keyword:
            raise exceptions.AuthenticationFailed("Authorization header format is invalid.")

        payload = decode_token(parts[1], expected_type="access")
        try:
            user = User.objects.get(pk=payload["sub"], is_active=True)
        except User.DoesNotExist as exc:
            raise exceptions.AuthenticationFailed("User not found.") from exc
        return (user, parts[1])

    def authenticate_header(self, request):
        return self.keyword
