from flask import Blueprint

from app.views.v1.user_view import UserView, TokenManagementView

# Define blueprints
v1_blueprints = Blueprint('v1', __name__)


# TokenManagement
v1_blueprints.add_url_rule(
    'token/refresh-token',
    view_func=TokenManagementView.refresh_access_token,
    methods=['POST'],
    endpoint='refresh_token'
)

# UserView Endpoints
v1_blueprints.add_url_rule(
    'user/signup', view_func=UserView.sign_up, methods=['POST'], endpoint='sign_up'
)
v1_blueprints.add_url_rule(
    'user/signin', view_func=UserView.sign_in, methods=['POST'], endpoint='sign_in'
)
v1_blueprints.add_url_rule(
    'user/details', view_func=UserView.get, methods=['GET'], endpoint='get_user_details'
)