from functools import wraps
from typing import Callable

from flask import request
import jwt
from app import logger, config_contents
from app.models.user import User
from app.helpers.utility import send_json_response
from app.helpers.constants import HttpStatusCode, ResponseMessageKeys, ResponseErrorCodes


def token_required(f: Callable) -> Callable:
    @wraps(f)
    def decorated(*args, **kwargs):
        """Validates the JWT token."""
        token = request.headers.get('Authorization')

        if not token or not token.startswith('Bearer '):
            return send_json_response(
                http_status=HttpStatusCode.UNAUTHORIZED.value,
                response_status=False,
                message_key=ResponseMessageKeys.INVALID_TOKEN.value,
                data=None,
                error=ResponseErrorCodes.INVALID_TOKEN.value
            )

        token = token.split(' ')[1]
        try:
            # Decode the token to get the user ID
            data = jwt.decode(token, key=config_contents['JWT']['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.get_by_id(id=data['id'])

            if not current_user:
                return send_json_response(
                    http_status=HttpStatusCode.UNAUTHORIZED.value,
                    response_status=False,
                    message_key=ResponseMessageKeys.INVALID_TOKEN.value,
                    data=None,
                    error=ResponseErrorCodes.INVALID_TOKEN.value
                )

        except jwt.ExpiredSignatureError:
            return send_json_response(
                http_status=HttpStatusCode.UNAUTHORIZED.value,
                response_status=False,
                message_key=ResponseMessageKeys.TOKEN_EXPIRED.value,
                data=None,
                error=ResponseErrorCodes.EXPIRED_TOKEN.value
            )
        except jwt.InvalidTokenError:
            return send_json_response(
                http_status=HttpStatusCode.UNAUTHORIZED.value,
                response_status=False,
                message_key=ResponseMessageKeys.INVALID_TOKEN.value,
                data=None,
                error=None
            )
        except Exception as e:
            logger.error('Error during token validation: %s', str(e))
            return send_json_response(
                http_status=HttpStatusCode.INTERNAL_SERVER_ERROR.value,
                response_status=False,
                message_key=ResponseMessageKeys.FAILED.value,
                data=None,
                error=ResponseErrorCodes.SERVER_ERROR.value
            )

        # Attach the user ID to the request for further use
        request.user_id = current_user.id
        return f(current_user, *args, **kwargs)

    return decorated
