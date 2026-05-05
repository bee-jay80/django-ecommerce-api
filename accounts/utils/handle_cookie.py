import jwt
from django.conf import settings

from rest_framework_simplejwt.tokens import RefreshToken


def create_session_token(user_id):
    # Ensure user_id is JSON-serializable (UUID -> str)
    payload = {
        'user_id': str(user_id),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token
    

def set_session_cookie(response, user_id):
    # Set the session token in the cookie with appropriate security settings
    token = create_session_token(user_id)
    response.set_cookie(
            key='session_token',
            value=token,
            max_age=900,  # Cookie expires in 15 minutes (900 seconds)
            secure=True,  # Ensure the cookie is only sent over HTTPS
            httponly=True,  # Prevent JavaScript access to the cookie
            samesite='None'  # 
        )
    return response

def set_access_refresh_token(response, user):
    refresh_token = RefreshToken.for_user(user)
    access_token = str(refresh_token.access_token)

    response.set_cookie(
        key='access_token',
        value=access_token,
        max_age=900,
        secure=True,
        httponly=True,
        samesite='None'
    )

    response.set_cookie(
        key='refresh_token',
        value=refresh_token,
        max_age=7 * 24 * 3600,  # 7 days,
        secure=True,
        httponly=True,
        samesite='None'
    )

    return response
