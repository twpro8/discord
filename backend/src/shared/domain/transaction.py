from typing import Protocol


class Transaction(Protocol):
    """Commits/rolls back the current request's unit of work.

    Structurally typed (not an ABC) so unit-test fakes satisfy it without
    subclassing. Most use cases never touch this directly — the request's
    session dependency auto-commits on a successful response (see
    api/v1/dependencies.py::get_transaction). A use case only depends on
    `Transaction` when it has work that must run strictly *after* its write
    is durable (a realtime publish, a cache invalidation, an enqueued job,
    ...); calling `commit()` there is what orders that work correctly.
    """

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...
