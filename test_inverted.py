import pytest

from base import get_session
from inverted import TestRepository, UserService, SQLARepository


@pytest.mark.parametrize(
    "repo",
    [TestRepository(), SQLARepository(session=get_session())],
    ids=["test-repo", "sqla-repo"],
)
def test_user_service(repo):
    svc = UserService(repo=repo)

    # create user
    user = svc.create_user("guido", "van rossum")
    result = repo.get(user.id)
    assert user is result

    # can retrieve user
    found = svc.get_user(user.id)
    assert user is found

    # delete user
    svc.delete_user(user)
    assert user.deleted_at is not None

    # cannot retrieve deleted user
    found = svc.get_user(user.id)
    assert found is None
