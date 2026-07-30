from typing import Protocol

from src.shared.application.query import Query


class QueryHandler[TQuery: Query, TResult](Protocol):
    async def handle(self, query: TQuery) -> TResult: ...
