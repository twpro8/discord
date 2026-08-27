class FakeTransaction:
    """Shared across modules' unit tests, replacing the per-module
    Fake<Name>UnitOfWork fakes — the real Transaction is auto-committed by
    the request's TransactionDep, so a use case only depends on this
    explicitly when it has work that must run strictly after the commit."""

    def __init__(self) -> None:
        self.committed = False
        self.rolled_back = False

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True
