import logging
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import authentication, exceptions
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

logger = logging.getLogger(__name__)


class CookieJWTAuthentication(authentication.BaseAuthentication):
    """Authenticate requests through JWTs stored in cookies.

    - Reads `access_token` from cookies and validates it.
    - If access token is expired or invalid, tries to use `refresh_token` from cookies to
      generate a fresh pair of tokens and attaches them to `request._new_tokens` so
      middleware can set cookies on the outgoing response.
    - Returns `(user, validated_token)` on success or `None` if no cookie present.
    """

    def authenticate(self, request):
        jwt_auth = JWTAuthentication()
        access_token = request.COOKIES.get("access_token")
        if not access_token:
            return None

        try:
            validated = jwt_auth.get_validated_token(access_token)
            user = jwt_auth.get_user(validated)
            return (user, validated)
        except Exception as e:
            # Try refresh flow when access token can't be validated
            logger.debug("Access token invalid: %s", e)

        # Attempt to refresh using refresh_token in cookie
        refresh_cookie = request.COOKIES.get("refresh_token")
        if not refresh_cookie:
            # No refresh available; authentication fails and upstream will handle
            raise exceptions.AuthenticationFailed("Invalid or expired access token.")

        try:
            # Validate the refresh token (this will raise if invalid/expired)
            refresh = RefreshToken(refresh_cookie)
        except TokenError as te:
            logger.info("Refresh token invalid or expired: %s", te)
            raise exceptions.AuthenticationFailed("Refresh token invalid or expired.")

        # Resolve user id claim
        user_id_claim = settings.SIMPLE_JWT.get("USER_ID_CLAIM", "user_id")
        user_id = refresh.payload.get(user_id_claim)
        if not user_id:
            raise exceptions.AuthenticationFailed("Refresh token missing user id claim")

        User = get_user_model()
        try:
            user = User.objects.get(**{settings.SIMPLE_JWT.get("USER_ID_FIELD", "id"): user_id})
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed("User not found")

        # Create new tokens (rotate by issuing fresh refresh token)
        new_refresh = RefreshToken.for_user(user)
        new_access = new_refresh.access_token

        # Attach new tokens to request for middleware to set cookies
        request._new_tokens = {
            "access": str(new_access),
            "refresh": str(new_refresh),
        }

        # Validate the new access token so we return a proper validated token
        try:
            validated = jwt_auth.get_validated_token(str(new_access))
            return (user, validated)
        except Exception as ex:
            logger.exception("Failed to validate newly created access token: %s", ex)
            raise exceptions.AuthenticationFailed("Failed to validate refreshed access token")
