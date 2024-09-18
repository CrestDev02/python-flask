from typing import Optional, Any

from app import db, logger


class Base(db.Model):
    """Base model for all other models with common methods for database interactions."""

    __abstract__ = True

    def save(self):
        """
        Save the instance to the database.
        """
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except Exception as e:
            logger.error(f'Error while saving instance: {e}')
            raise

    @classmethod
    def get_by_id(cls, id: int) -> Any:
        """Retrieve a record by its primary key.

        Args:
            id (int): The primary key of the record to retrieve.

        Returns:
            Any: The record if found, otherwise None.
        """
        return cls.query.get(id)
