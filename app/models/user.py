import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import UUID

from app import db, logger
from app.models.base import Base

class User(Base):
    """
    Represents a user in the system, storing personal information such as name, email, and timestamps.
    """

    __tablename__ = 'users'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    uuid = db.Column(UUID(as_uuid=True), unique=True, default=uuid.uuid4, nullable=False)

    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)

    last_login_at = db.Column(db.DateTime, nullable=True)
    deactivated_at = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    def __init__(
            self,
            name: str,
            email: str,
            password: str,
            last_login_at: Optional[datetime] = None,
            deactivated_at: Optional[datetime] = None
    ):
        """
        Initialize a User instance with mandatory and optional fields.

        Args:
            name (str): The user's name.
            email (str): The user's email address.
            email (str): The user's password.
            last_login_at (Optional[datetime]): The user's last login timestamp, default is None.
            deactivated_at (Optional[datetime]): The user's deactivation timestamp, default is None.
        """
        self.name = name
        self.email = email
        self.password = password
        self.last_login_at = last_login_at
        self.deactivated_at = deactivated_at

    def __repr__(self) -> str:
        """
        Provide a string representation of the User instance for debugging.

        Returns:
            str: A string representation of the User instance.
        """
        return f'<User(id={self.id}, name={self.name})>'

    @classmethod
    def get_by_email(cls, email: str) -> 'User':
        """
            Filter records by email.

            Args:
                email (str): The email of the user to filter by.

            Returns:
                Any: The User object corresponding to the given email.
        """
        return db.session.query(
            User
        ).filter(
            User.email == email
        ).first()

    @classmethod
    def user_to_dict(cls, user: 'User') -> dict:
        return {
            'id': user.id,
            'uuid': str(user.uuid),
            'name': user.name,
            'email': user.email,
            'last_login_at': user.last_login_at.isoformat() if user.last_login_at else None,
            'deactivated_at': user.deactivated_at.isoformat() if user.deactivated_at else None,
            'created_at': user.created_at.isoformat(),
            'updated_at': user.updated_at.isoformat() if user.updated_at else None,
        }

    def update_last_login(self) -> None:
        """
        Update the last login timestamp to the current time.
        """
        self.last_login_at = datetime.utcnow()
        db.session.commit()

    def deactivate(self) -> None:
        """
        Mark the user as deactivated and update the deactivation timestamp.
        """
        self.deactivated_at = datetime.utcnow()
        db.session.commit()
