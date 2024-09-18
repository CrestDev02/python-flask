import enum


class HttpStatusCode(enum.Enum):
    """Enum for HTTP status codes used in REST APIs."""

    # 2xx Success
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204

    # 4xx Client Errors
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404

    # 5xx Server Errors
    INTERNAL_SERVER_ERROR = 500


class ResponseErrorCodes(enum.Enum):
    EMAIL_EXISTS = 'EMAIL_EXISTS'
    USERNAME_EXISTS = 'USERNAME_EXISTS'
    INVALID_CREDENTIALS = 'INVALID_CREDENTIALS'
    INSUFFICIENT_DATA = 'INSUFFICIENT_DATA'
    INVALID_TOKEN = 'INVALID_TOKEN'
    EXPIRED_TOKEN = 'EXPIRED_TOKEN'
    SERVER_ERROR = 'SERVER_ERROR'
    NOT_FOUND = 'NOT_FOUND'
    SUCCESS = 'SUCCESS'



class ResponseMessageKeys(enum.Enum):
    """Enum for storing common response messages used in REST API responses."""

    # Success Messages
    SUCCESS = 'Request completed successfully.'
    CREATED = 'Resource created successfully.'
    UPDATED = 'Resource updated successfully.'
    DELETED = 'Resource deleted successfully.'
    LOGIN_SUCCESS = 'Login successful!'

    # Client Error Messages
    EMAIL_EXISTS = 'The email address is already in use. Please use a different email address.'
    USERNAME_EXISTS = 'The username is already taken. Please choose a different username.'
    INVALID_CREDENTIALS = 'Provided email or password is invalid.'
    INVALID_REFRESH_TOKEN = 'The provided refresh token is invalid or missing.'
    REFRESH_TOKEN_EXPIRED = 'The refresh token has expired.'
    TOKEN_REFRESHED = 'Access token successfully refreshed.'
    INVALID_TOKEN = 'The provided access token is invalid or missing.'
    TOKEN_EXPIRED = 'The access token has expired.'
    USER_DOES_NOT_EXIST = 'No account found with the provided credentials. Please register for an account.'

    # Server Error Messages
    FAILED = 'Something went wrong. Please try again later.'
    INTERNAL_SERVER_ERROR = 'The server encountered an internal error. Please contact support.'


class ValidationMessages:
    messages = {
        'EMAIL': 'Email address is required.',
        'NAME': 'Name is required.',
        'PASSWORD': 'Password is required.',
    }

    @classmethod
    def get_message(cls, key: str) -> str:
        return cls.messages.get(key.upper(), f'{key.replace("_", " ").title()} is required.')