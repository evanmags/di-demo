from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import Table, Column
from sqlalchemy.orm import Session, registry
from sqlalchemy.types import String, DateTime

from base import metadata, engine

# region domain model
@dataclass
class User:
    id: str = field(init=False, default="")
    first_name: str
    last_name: str
    created_at: datetime
    deleted_at: Optional[datetime] = field(init=False, default=None)
# endregion

# region data layer
mappers = registry()

users_table = Table(
    "users",
    metadata,
    Column("id", String, primary_key=True, default=lambda: uuid4().hex),
    Column("first_name", String, nullable=False),
    Column("last_name", String, nullable=False),
    Column("created_at", DateTime, nullable=False),
    Column("deleted_at", DateTime),
)

mappers.map_imperatively(User, users_table)
metadata.create_all(engine)
# endregion

# region repository
class UserRepository(ABC):
    @abstractmethod
    def get(self, user_id: str) -> Optional[User]:
        ...

    @abstractmethod
    def set(self, user: User) -> User:
        ...


class SQLARepository(UserRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, user_id: str):
        return (
            self._session.query(User)
            .filter(User.id == user_id, User.deleted_at == None)
            .one_or_none()
        )

    def set(self, user: User):
        self._session.add(user)
        self._session.flush()
        return user


class TestRepository(UserRepository):
    _users: list[User] = []

    def get(self, user_id: str) -> Optional[User]:
        for user in self._users:
            if user.id == user_id:
                return user if user.deleted_at is None else None

        return None

    def set(self, user: User) -> User:
        # mock auto creation of id
        if not user.id:
            user.id = uuid4().hex

        self._users = [u for u in self._users if u.id != user.id]
        self._users.append(user)
        return user


# endregion

# region service
class UserService:
    def __init__(self, repo: UserRepository):
        self._repo = repo

    def create_user(self, first_name: str, last_name: str) -> User:
        user = User(
            first_name=first_name,
            last_name=last_name,
            created_at=datetime.now(),
        )
        return self.save_user(user)

    def save_user(self, user: User) -> User:
        return self._repo.set(user)

    def get_user(self, user_id: str) -> Optional[User]:
        return self._repo.get(user_id)

    def delete_user(self, user: User):
        if user.deleted_at is None:
            user.deleted_at = datetime.now()
            self._repo.set(user)


# endregion
