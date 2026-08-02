import pytest

from src.shared.result import Result


def test_ok_result_exposes_value() -> None:
    result: Result[int, str] = Result.ok(42)

    assert result.is_ok
    assert not result.is_err
    assert result.value == 42


def test_err_result_exposes_error() -> None:
    result: Result[int, str] = Result.err("boom")

    assert result.is_err
    assert not result.is_ok
    assert result.error == "boom"


def test_ok_result_raises_on_error_access() -> None:
    result: Result[int, str] = Result.ok(42)

    with pytest.raises(ValueError):
        _ = result.error


def test_err_result_raises_on_value_access() -> None:
    result: Result[int, str] = Result.err("boom")

    with pytest.raises(ValueError):
        _ = result.value
