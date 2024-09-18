from datetime import datetime, timezone, timedelta

import jwt
from flask import jsonify
from typing import Any, Optional, Dict, Tuple, List

from app import config_contents
from app.helpers.constants import ValidationMessages


def validate_required_fields(
        request_data: Optional[Dict[str, Any]] = None,
        required_fields: Optional[List[str]] = None,
        prefix: Optional[str] = None
) -> Dict[str, Any]:
    """
    Validate that all required fields are present in the given data dictionary.

    Args:
        request_data (Dict[str, Any]): Data to validate.
        required_fields (List[str]): List of required fields.
        prefix (Optional[str]): Optional prefix for the error message.

    Returns:
        Dict[str, Any]: Contains 'is_error' key indicating if there are errors and 'data' key with error messages.
    """
    if required_fields is None:
        required_fields = []
    if request_data is None:
        request_data = {}

    errors = {}
    for field in required_fields:
        value = request_data.get(field)
        if value in [None, '']:
            # Determine error message
            if prefix:
                message = f'{prefix} {field.replace("_", " ").title()} is required.'
            else:
                message = ValidationMessages.get_message(field)
            errors[field] = message

    return {
        'is_error': bool(errors),
        'data': errors
    }

def send_json_response(
        http_status: int,
        response_status: bool,
        message_key: str,
        data: Optional[Any] = None,
        error: Optional[Any] = None,
        extra_fields: Optional[Dict[str, Any]] = None
) -> Tuple:
    """
    This method sends a JSON response in a custom structure.

    :param http_status: HTTP response status code.
    :param response_status: Boolean indicating success or failure.
    :param message_key: Message string to be included in the response.
    :param data: Optional, response data to be included (default is None).
    :param error: Optional, error details to be included if the response failed (default is None).
    :param extra_fields: Optional, dictionary of any additional fields you may want to include in the response.
    :return: Tuple containing the JSON response and HTTP status code.
    """

    # Map the response_status to a more descriptive status value
    status_str = 'success' if response_status else 'error'

    # Base structure of the response
    response = {
        'status': status_str,
        'message': message_key
    }

    # If the response is successful, include data
    if response_status and data is not None:
        response['data'] = data

    # If there's an error, include it in the response
    elif not response_status and error is not None:
        response['error'] = error

    # Add any extra fields if they are passed
    if extra_fields:
        response.update(extra_fields)

    # Return the JSON response along with the HTTP status code
    return jsonify(response), http_status

def generate_email_token(user_id: int):
    """
        Generate an email token for the given UUID.

        Args:
            user_id (int): The user id for which the token is generated.

        Returns:
            str: The generated email token.
    """
    secret = config_contents['SECRET_KEY']
    current_utc_timestamp = datetime.now(tz=timezone.utc)
    data = {
        'timestamp': int(current_utc_timestamp.timestamp()),
        'id': user_id,
        'exp': int((current_utc_timestamp + timedelta(hours=60)).timestamp())
    }
    token = jwt.encode(payload=data, key=secret)
    return token