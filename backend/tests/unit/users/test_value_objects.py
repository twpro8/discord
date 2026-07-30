import pytest

from src.modules.users.domain.exceptions import InvalidEmail, InvalidUsername
from src.modules.users.domain.value_objects.email import Email
from src.modules.users.domain.value_objects.username import Username


def test_email_normalizes_case_and_whitespace() -> None:
    assert str(Email("  Alice@Example.COM  ")) == "alice@example.com"


def test_email_rejects_invalid_format() -> None:
    with pytest.raises(InvalidEmail):
        Email("not-an-email")


def test_username_normalizes_whitespace() -> None:
    assert str(Username("  alice  ")) == "alice"


@pytest.mark.parametrize("value", ["ab", "a" * 33])
def test_username_rejects_out_of_range_length(value: str) -> None:
    with pytest.raises(InvalidUsername):
        Username(value)


def test_username_accepts_boundary_lengths() -> None:
    assert str(Username("abc")) == "abc"
    assert str(Username("a" * 32)) == "a" * 32
