from dataclasses import dataclass


@dataclass(frozen=True)
class Result[T, E]:
    """Explicit success/failure container for application-layer use cases.

    Use for expected, "business" failures (validation, policy violations,
    not-found) that the presentation layer should map to a specific HTTP
    status. Reserve real exceptions for unexpected/programmer errors.

        result = await mediator.send(RegisterUserCommand(...))
        if result.is_err:
            raise HTTPException(400, detail=str(result.error))
        return result.value
    """

    _value: T | None
    _error: E | None
    is_ok: bool

    @classmethod
    def ok(cls, value: T) -> Result[T, E]:
        return cls(_value=value, _error=None, is_ok=True)

    @classmethod
    def err(cls, error: E) -> Result[T, E]:
        return cls(_value=None, _error=error, is_ok=False)

    @property
    def is_err(self) -> bool:
        return not self.is_ok

    @property
    def value(self) -> T:
        if not self.is_ok:
            raise ValueError(
                f"Cannot access .value on an error Result: {self._error!r}"
            )
        return self._value  # type: ignore[return-value]

    @property
    def error(self) -> E:
        if self.is_ok:
            raise ValueError("Cannot access .error on an ok Result")
        return self._error  # type: ignore[return-value]
