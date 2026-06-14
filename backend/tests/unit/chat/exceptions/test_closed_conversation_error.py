from __future__ import annotations

import pytest

from src.chat.exceptions.closed_conversation_error import ClosedConversationError


class TestClosedConversationError:
    def test_can_be_instantiated(self) -> None:
        err = ClosedConversationError("conversation is closed")
        assert str(err) == "conversation is closed"

    def test_is_exception_subclass(self) -> None:
        assert issubclass(ClosedConversationError, Exception)

    def test_can_be_raised_and_caught(self) -> None:
        with pytest.raises(ClosedConversationError):
            raise ClosedConversationError("closed")
