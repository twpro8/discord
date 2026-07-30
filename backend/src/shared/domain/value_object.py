from dataclasses import dataclass


@dataclass(frozen=True)
class ValueObject:
    """Base marker for value objects.

    Value objects are immutable and compared by value, not identity.
    Subclass as a frozen dataclass:

        @dataclass(frozen=True)
        class Email(ValueObject):
            value: str

            def __post_init__(self):
                if "@" not in self.value:
                    raise InvalidEmail(self.value)
    """
