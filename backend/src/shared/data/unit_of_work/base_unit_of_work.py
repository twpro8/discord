from sqlalchemy.ext.asyncio import AsyncSession


class BaseUnitOfWork:
    """
    Base class for implementing the Unit of Work pattern.

    This class provides transactional control methods such as commit and
    rollback over a SQLAlchemy async session. It does NOT own the session's
    lifecycle: a single request's `AsyncSession` is shared across several
    per-module UnitOfWork instances (one per composition.py that needs it),
    so closing or rolling back the session here would step on the other
    instances sharing it. Session close and exception-triggered rollback are
    owned solely by the request-scoped `get_session` dependency
    (`core/database/session.py`), which is the only code that knows when the
    session's owning request has actually ended.

    The class is intentionally abstract and must not be instantiated directly.
    Concrete Unit of Work implementations should inherit from this class and
    initialize domain-specific repositories inside their constructors.

    Example:
        class UserUnitOfWork(BaseUnitOfWork):
            def __init__(
                self,
                session: AsyncSession,
                user_repository: UserRepository,
                # other repositories if needed
            ) -> None:
                super().__init__(session)
                self.users = user_repository

        uow = UserUnitOfWork(session)
        await uow.users.create(user_data)
        await uow.commit()

    Attributes:
        _session:
            Active SQLAlchemy asynchronous session used by repositories.
    """

    _session: AsyncSession

    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize the Unit of Work with an async database session.

        Args:
            session:
                SQLAlchemy asynchronous session instance.
        """
        self._session = session

    async def commit(self) -> None:
        """
        Commit the current transaction.
        """
        await self._session.commit()

    async def rollback(self) -> None:
        """
        Roll back the current transaction.
        """
        await self._session.rollback()
