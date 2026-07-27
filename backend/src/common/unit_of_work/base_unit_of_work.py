from abc import ABC, abstractmethod
from types import TracebackType
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession


class BaseUnitOfWork(ABC):
    """
    Base class for implementing the Unit of Work pattern.

    This class manages the lifecycle of a SQLAlchemy async session and provides
    transactional control methods such as commit and rollback. It is designed
    to be used as an asynchronous context manager.

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

            def _uow_marker(self) -> None: ...

        async with UserUnitOfWork(session) as uow:
            await uow.users.create(user_data)
            await uow.commit()

    Attributes:
        _session:
            Active SQLAlchemy asynchronous session used by repositories.

    Notes:
        - On successful execution, the session is simply closed.
        - If an exception occurs inside the context manager block,
          the transaction is rolled back automatically.
        - Repositories should reuse the same session instance provided
          by the Unit of Work.
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

    async def __aenter__(self) -> Self:
        """
        Enter the asynchronous context manager.

        Returns:
            Current Unit of Work instance.
        """
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """
        Exit the asynchronous context manager.

        Rolls back the current transaction if an exception occurred and
        closes the database session afterward.

        Args:
            exc_type:
                Exception type if raised inside the context manager.
            exc_val:
                Exception instance.
            exc_tb:
                Exception traceback.
        """
        if exc_type:
            await self._session.rollback()
        await self._session.close()

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

    @abstractmethod
    def _uow_marker(self) -> None:
        """
        Prevent direct instantiation of the base Unit of Work class.
        """
