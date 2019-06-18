import jwt
from datetime import datetime, timedelta
from authors.settings import SECRET_KEY
from rest_framework import exceptions

class AuthenticationToken:
    def encode_auth_token(self, pk):
        payload = {
            "exp": datetime.utcnow() + timedelta(days=30),
            "iat": datetime.utcnow(),
            "id": pk
        }
        return (jwt.encode(payload, SECRET_KEY, algorithm='HS256')).decode("utf-8")

    def decode_auth_token(self, token):
        try:
            payload = jwt.decode(token, SECRET_KEY)
            return payload['id']
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            raise exceptions.AuthenticationFailed("Token invalid or expired. please login again.")
