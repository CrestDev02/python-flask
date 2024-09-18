import traceback
from datetime import datetime, timedelta

import jwt
from flask import request
from flask.views import View

from werkzeug.security import generate_password_hash, check_password_hash

from app import logger, config_contents
from app.helpers.decorators import token_required
from app.models.user import User
from app.helpers.utility import send_json_response, validate_required_fields
from app.helpers.constants import HttpStatusCode, ResponseMessageKeys, ResponseErrorCodes


class TokenManagementView(View):
    @staticmethod
    def create_token(user_id, email, expiration_minutes):
        """
        Helper method to create a JWT token.

        Args:
            user_id (int): The ID of the user.
            email (str): The email of the user.
            expiration_minutes (int): The expiration time in minutes.

        Returns:
            str: The encoded JWT token.
        """
        exp_time = datetime.utcnow() + timedelta(minutes=expiration_minutes)
        return jwt.encode({
            'id': user_id,
            'email': email,
            'exp': exp_time
        }, key=config_contents['JWT']['SECRET_KEY'])

    @staticmethod
    def refresh_access_token():
        """
        Refresh the access token using a valid refresh token.
        """
        data = request.get_json()
        refresh_token = data.get('refresh_token')

        if not refresh_token:
            return send_json_response(
                http_status=HttpStatusCode.BAD_REQUEST.value,
                response_status=False,
                message_key=ResponseMessageKeys.INVALID_REFRESH_TOKEN.value,
                data=None,
                error=ResponseErrorCodes.INVALID_TOKEN.value
            )

        try:
            # Decode the refresh token
            decoded_token = jwt.decode(refresh_token, key=config_contents['JWT']['SECRET_KEY'], algorithms=['HS256'])
            user_id = decoded_token['id']

            # Fetch user and generate new access token
            user = User.get_by_id(user_id)
            if not user:
                return send_json_response(
                    http_status=HttpStatusCode.UNAUTHORIZED.value,
                    response_status=False,
                    message_key=ResponseMessageKeys.INVALID_REFRESH_TOKEN.value,
                    data=None,
                    error=ResponseErrorCodes.INVALID_TOKEN.value
                )

            new_access_token = TokenManagementView.create_token(
                user_id=user.id, email=user.email, expiration_minutes=config_contents['JWT']['ACCESS_TOKEN_EXPIRE']
            )

            return send_json_response(
                http_status=HttpStatusCode.OK.value,
                response_status=True,
                message_key=ResponseMessageKeys.TOKEN_REFRESHED.value,
                data={'access_token': new_access_token},
                error=None
            )
        except jwt.ExpiredSignatureError:
            return send_json_response(
                http_status=HttpStatusCode.UNAUTHORIZED.value,
                response_status=False,
                message_key=ResponseMessageKeys.REFRESH_TOKEN_EXPIRED.value,
                data=None,
                error=ResponseErrorCodes.EXPIRED_TOKEN.value
            )
        except jwt.InvalidTokenError:
            return send_json_response(
                http_status=HttpStatusCode.UNAUTHORIZED.value,
                response_status=False,
                message_key=ResponseMessageKeys.INVALID_REFRESH_TOKEN.value,
                data=None,
                error=ResponseErrorCodes.INVALID_TOKEN.value
            )
        except Exception as e:
            logger.error(
                'Error refreshing token: %s\n%s',
                str(e),
                traceback.format_exc()
            )
            return send_json_response(
                http_status=HttpStatusCode.INTERNAL_SERVER_ERROR.value,
                response_status=False,
                message_key=ResponseMessageKeys.FAILED.value,
                data=None,
                error=ResponseErrorCodes.SERVER_ERROR.value
            )


class UserView(View):
    @staticmethod
    def create_auth_response(user: User) -> dict:
        """
        Creates a response containing user details and an authentication token.

        Args:
            user (User): The user object for whom the authentication response is created.

        Returns:
            dict: A dictionary containing 'access_token', 'refresh_token', and 'details' (user details).
        """
        access_token = TokenManagementView.create_token(
            user_id=user.id, email=user.email, expiration_minutes=config_contents['JWT']['ACCESS_TOKEN_EXPIRE']
        )
        refresh_token = TokenManagementView.create_token(
            user_id=user.id, email=user.email, expiration_minutes=config_contents['JWT']['REFRESH_TOKEN_EXPIRE']
        )

        user_details = User.user_to_dict(user=user)
        return {'access_token': access_token, 'refresh_token': refresh_token, 'details': user_details}


    @staticmethod
    def sign_up():
        """
        Handle user registration.

        Request Body:
            - name (str): The name of the user.
            - email (str): The email address of the user.
            - password (str): The password for the user account.
        """
        try:
            data = request.get_json()

            # Required fields
            required_fields = ['name', 'email', 'password']

            # Validate input fields
            validation_result = validate_required_fields(data, required_fields)
            if validation_result['is_error']:
                return send_json_response(
                    http_status=HttpStatusCode.BAD_REQUEST.value,
                    response_status=False,
                    message_key=validation_result['data'],
                    data=None,
                    error=ResponseErrorCodes.INSUFFICIENT_DATA.value
                )

            name = data['name']
            email = data['email']
            password = data['password']

            # Check if user already exists
            if User.get_by_email(email=email):
                return send_json_response(
                    http_status=HttpStatusCode.BAD_REQUEST.value,
                    response_status=False,
                    message_key=ResponseMessageKeys.EMAIL_EXISTS.value,
                    data=None,
                    error=ResponseErrorCodes.EMAIL_EXISTS.value
                )

            # Create and save the new user
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            user = User(name=name, email=email, password=hashed_password)
            user.save()

            user_data = User.user_to_dict(user=user)

            return send_json_response(
                http_status=HttpStatusCode.CREATED.value,
                response_status=True,
                message_key=ResponseMessageKeys.CREATED.value,
                data=user_data,
                error=None
            )
        except Exception as e:
            logger.error(
                'Error occurred while registering user. Exception details: %s\n%s',
                str(e),
                traceback.format_exc()
            )
            return send_json_response(
                http_status=HttpStatusCode.INTERNAL_SERVER_ERROR.value,
                response_status=False,
                message_key=ResponseMessageKeys.FAILED.value,
                data=None,
                error=ResponseErrorCodes.SERVER_ERROR.value
            )

    @staticmethod
    def sign_in():
        """
        Handle user sign-in.

        Request Body:
            - email (str): The email address of the user.
            - password (str): The password for the user account.
        """
        try:
            data = request.get_json()
            required_fields = ['email', 'password']

            # Validate input fields
            validation_result = validate_required_fields(data, required_fields)
            if validation_result['is_error']:
                return send_json_response(
                    http_status=HttpStatusCode.BAD_REQUEST.value,
                    response_status=False,
                    message_key=validation_result['data'],
                    data=None,
                    error=ResponseErrorCodes.INSUFFICIENT_DATA.value
                )

            email = data['email']
            password = data['password']

            # Fetch the user by email
            user = User.get_by_email(email=email)
            if not user or not check_password_hash(user.password, password):
                return send_json_response(
                    http_status=HttpStatusCode.UNAUTHORIZED.value,
                    response_status=False,
                    message_key=ResponseMessageKeys.INVALID_CREDENTIALS.value,
                    data=None,
                    error=ResponseErrorCodes.INVALID_CREDENTIALS.value
                )

            user_data = UserView.create_auth_response(user=user)

            # Update last login time
            user.update_last_login()

            return send_json_response(
                http_status=HttpStatusCode.OK.value,
                response_status=True,
                message_key=ResponseMessageKeys.LOGIN_SUCCESS.value,
                data=user_data,
                error=ResponseErrorCodes.SUCCESS.value
            )
        except Exception as e:
            logger.error(
                'Error occurred while logging the user in. Exception details: %s\n%s',
                str(e),
                traceback.format_exc()
            )
            return send_json_response(
                http_status=HttpStatusCode.INTERNAL_SERVER_ERROR.value,
                response_status=False,
                message_key=ResponseMessageKeys.FAILED.value,
                data=None,
                error=ResponseErrorCodes.SERVER_ERROR.value
            )

    @staticmethod
    @token_required
    def get(current_user: User):
        """
        Get user details for the authenticated user.

        Returns:
            JSON response containing user details.
        """
        try:
            # Get the current user's identity from the JWT
            current_user_id = current_user.id

            # Fetch user from the database
            user = User.get_by_id(current_user_id)

            if not user:
                return send_json_response(
                    http_status=HttpStatusCode.NOT_FOUND.value,
                    response_status=False,
                    message_key=ResponseMessageKeys.USER_DOES_NOT_EXIST.value,
                    data=None,
                    error=ResponseErrorCodes.NOT_FOUND.value
                )

            user_data = User.user_to_dict(user=user)

            return send_json_response(
                http_status=HttpStatusCode.OK.value,
                response_status=True,
                message_key=ResponseMessageKeys.SUCCESS.value,
                data=user_data,
                error=None
            )
        except Exception as e:
            logger.error(
                'Error occurred while fetching user details: %s\n%s',
                str(e),
                traceback.format_exc()
            )
            return send_json_response(
                http_status=HttpStatusCode.INTERNAL_SERVER_ERROR.value,
                response_status=False,
                message_key=ResponseMessageKeys.FAILED.value,
                data=None,
                error=ResponseErrorCodes.SERVER_ERROR.value
            )