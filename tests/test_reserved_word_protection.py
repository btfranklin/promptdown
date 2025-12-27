import pytest
from promptdown import Message


def test_disallow_system_role_in_messages():
    with pytest.raises(ValueError) as excinfo:
        _ = Message(role="System", content="This should not be allowed.")
    assert "reserved and cannot be used" in str(excinfo.value)

    with pytest.raises(ValueError):
        _ = Message(
            role="system",
            content="This should not be allowed, either.",
        )

    with pytest.raises(ValueError):
        _ = Message(role="SYSTEM", content="Nor should this.")


def test_valid_role_in_messages():
    # This should pass without issues
    try:
        _ = Message(role="User", content="This is fine.")
        _ = Message(role="Assistant", content="This is also fine.")
    except ValueError:
        pytest.fail("Unexpected ValueError for valid roles.")
