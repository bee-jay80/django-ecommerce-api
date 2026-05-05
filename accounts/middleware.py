from django.utils.deprecation import MiddlewareMixin
from django.conf import settings


class RefreshTokenMiddleware(MiddlewareMixin):
    """If `request._new_tokens` exists (set by CookieJWTAuthentication), write cookies
    for `access_token` and `refresh_token` on the outgoing response.
    """

    def process_response(self, request, response):
        new = getattr(request, "_new_tokens", None)
        if not new:
            return response

        # secure_flag = not settings.DEBUG
        # samesite = "None" if secure_flag else "Lax"

        # Set access token cookie
        response.set_cookie(
            key="access_token",
            value=new.get("access"),
            max_age=900,
            secure=True,
            httponly=True,
            samesite="None",
        )

        # Set refresh token cookie (longer expiry or use default from settings)
        response.set_cookie(
            key="refresh_token",
            value=new.get("refresh"),
            max_age=7 * 24 * 3600,  # 7 days
            secure=True,
            httponly=True,
            samesite="None",
        )

        return response
