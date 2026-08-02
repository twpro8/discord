"""Integration tests for BaseUnitOfWork's session-sharing contract.

Regression coverage for the get_mediator pattern: several per-module
UnitOfWork instances are constructed directly (no context-manager protocol,
no AsyncExitStack) against one shared, physical request-scoped session.
BaseUnitOfWork itself owns none of that session's lifecycle -- only the
request boundary (get_session) may commit/rollback/close it -- so sibling
UoWs must be free to read each other's uncommitted writes through the
shared session, and a UoW going out of scope must have no side effects on
it whatsoever.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.users.domain.entities.user import User
from src.modules.users.domain.value_objects.email import Email
from src.modules.users.domain.value_objects.username import Username
from src.modules.users.infrastructure.persistence.user_repository_impl import (
    UserRepositoryImpl,
)
from src.shared.data.unit_of_work.base_unit_of_work import BaseUnitOfWork


class _FakeUnitOfWork(BaseUnitOfWork):
    def __init__(
        self, session: AsyncSession, user_repository: UserRepositoryImpl
    ) -> None:
        super().__init__(session)
        self.users = user_repository


def _make_user() -> User:
    unique = uuid.uuid4().hex[:8]
    return User.register(
        name="Test User",
        email=Email(f"{unique}@example.com"),
        username=Username(f"user_{unique}"),
        password_hash="hashed",
    )


def test_unit_of_work_is_not_a_context_manager() -> None:
    """BaseUnitOfWork must not expose __aenter__/__aexit__: nothing should
    be able to reintroduce the old close-the-shared-session-on-exit bug by
    wrapping a UoW in `async with`.
    """
    assert not hasattr(BaseUnitOfWork, "__aenter__")
    assert not hasattr(BaseUnitOfWork, "__aexit__")


async def test_sibling_uows_share_one_session_and_see_each_others_writes(
    session: AsyncSession,
) -> None:
    """Mirrors get_mediator's real pattern: each module's composition.py
    constructs its own UnitOfWork directly against the same session. A
    write through one must be visible to a sibling before either commits,
    and constructing/discarding a UoW must not touch the session at all.
    """
    repository = UserRepositoryImpl(session)
    user = _make_user()

    first_uow = _FakeUnitOfWork(session, repository)
    second_uow = _FakeUnitOfWork(session, repository)

    await first_uow.users.add(user)

    # second_uow shares the same session -- the uncommitted write is
    # visible to it without any commit having happened yet.
    assert (await second_uow.users.get_by_id(user.id)) is not None

    await first_uow.commit()
    assert (await repository.get_by_id(user.id)) is not None

    await session.rollback()
    await session.close()
