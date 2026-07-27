import jwt

from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class TorobJWTAuthentication(BaseAuthentication):
    """
    اعتبارسنجی JWT ارسالی ترب از طریق هدر X-Torob-Token
    """

    def authenticate(self, request):
        auth_enabled = getattr(settings, "TOROB_API_AUTH_ENABLED", True)

        # برای تست لوکال، اگر خواستی می‌توانی در settings غیرفعالش کنی
        if not auth_enabled:
            return None

        token = request.headers.get("X-Torob-Token")
        token_version = request.headers.get("X-Torob-Token-Version")

        if not token:
            raise AuthenticationFailed("missing X-Torob-Token header")

        if not token_version:
            raise AuthenticationFailed("missing X-Torob-Token-Version header")

        expected_version = getattr(settings, "TOROB_TOKEN_VERSION", "1")

        if str(token_version) != str(expected_version):
            raise AuthenticationFailed("invalid X-Torob-Token-Version header")

        public_key = getattr(settings, "TOROB_PUBLIC_KEY", None)

        if not public_key:
            raise AuthenticationFailed("torob public key is not configured")

        expected_audience = getattr(settings, "TOROB_EXPECTED_AUDIENCE", None)

        if not expected_audience:
            # اگر در settings مقدار aud مشخص نشده بود، از Host درخواست استفاده می‌کنیم
            expected_audience = request.get_host()

        try:
            # خواندن header توکن بدون اعتبارسنجی، فقط برای چک اولیه
            unverified_header = jwt.get_unverified_header(token)

            if unverified_header.get("alg") != "EdDSA":
                raise AuthenticationFailed("invalid token algorithm")

            if str(unverified_header.get("v")) != str(expected_version):
                raise AuthenticationFailed("invalid token header version")

            payload = jwt.decode(
                token,
                key=public_key,
                algorithms=["EdDSA"],
                audience=expected_audience,
                leeway=30,
            )

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("token has expired")

        except jwt.ImmatureSignatureError:
            raise AuthenticationFailed("token is not valid yet")

        except jwt.InvalidAudienceError:
            raise AuthenticationFailed("invalid token audience")

        except jwt.InvalidSignatureError:
            raise AuthenticationFailed("invalid token signature")

        except jwt.DecodeError:
            raise AuthenticationFailed("invalid token format")

        except jwt.InvalidTokenError:
            raise AuthenticationFailed("invalid token")

        request.torob_token_payload = payload

        # چون کاربر واقعی نداریم، یک tuple برمی‌گردانیم.
        # user را None می‌گذاریم و auth را payload.
        return None, payload
