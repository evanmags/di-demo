from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import Column
from sqlalchemy.types import String, DateTime

from base import get_session, Base

session = get_session()

# region data/domain
class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: uuid4().hex)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    deleted_at = Column(DateTime, default=None)
# endregion

# region repository
class UserRepository:
    @staticmethod
    def get(user_id: str):
        return (
            session.query(User)
            .filter(User.id == user_id, User.deleted_at == None)
            .one_or_none()
        )

    @staticmethod
    def set(user: User):
        session.add(user)
        session.flush()
        return user
# endregion

# region service
class UserService:
    @staticmethod
    def create_user(first_name: str, last_name: str) -> User:
        user = User(
            first_name=first_name,
            last_name=last_name,
            created_at=datetime.now(),
        )
        return UserRepository.set(user)

    @staticmethod
    def save_user(user: User) -> User:
        return UserRepository.set(user)

    @staticmethod
    def get_user(user_id: str) -> Optional[User]:
        return UserRepository.get(user_id)

    @staticmethod
    def delete_user(user: User):
        if user.deleted_at is None:
            user.deleted_at = datetime.now()  # type: ignore
            UserRepository.set(user)
# endregion
