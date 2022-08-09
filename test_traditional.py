from datetime import datetime
from unittest.mock import patch
from uuid import uuid4

import pytest

from traditional import UserRepository, UserService, User


def test_user_service_integration():
    # create user
    user = UserService.create_user("guido", "van rossum")
    result = UserRepository.get(user.id)  # type: ignore
    assert user is result

    # can retrieve user
    found = UserService.get_user(user.id)  # type: ignore
    assert user is found

    # delete user
    UserService.delete_user(user)
    assert user.deleted_at is not None

    # cannot retrieve deleted user
    found = UserService.get_user(user.id)  # type: ignore
    assert found is None


mock_user_data = {
    "id": uuid4().hex,
    "first_name": "guido",
    "last_name": "guido",
    "created_at": datetime.now(),
    "deleted_at": None,
}


@pytest.fixture
def mock_user_repo():
    def _mock_set(user: User):
        if not user.id:
            user.id = mock_user_data["id"]
        return user

    def _mock_get(user_id: str):
        return User(
            id=user_id,
            first_name=mock_user_data["first_name"],
            last_name=mock_user_data["last_name"],
            created_at=mock_user_data["created_at"],
            deleted_at=mock_user_data["deleted_at"],
        )

    with patch("traditional.UserRepository", autospec=UserRepository) as mock:
        mock.set.side_effect = _mock_set
        mock.get.side_effect = _mock_get

        yield mock


def test_user_service_unit(mock_user_repo):
    user = UserService.create_user("guido", "van rossum")
    assert user.id is not None
    mock_user_repo.set.assert_called()

    user = UserService.get_user(user.id)  # type: ignore
    mock_user_repo.get.assert_called_with(user.id)  # type: ignore

    # delete user
    UserService.delete_user(user)
    assert user.deleted_at is not None  # type: ignore
    mock_user_repo.set.assert_called()

    # cannot retrieve deleted user
    found = UserService.get_user(user.id)  # type: ignore
    mock_user_repo.get.assert_called_with(user.id)  # type: ignore
