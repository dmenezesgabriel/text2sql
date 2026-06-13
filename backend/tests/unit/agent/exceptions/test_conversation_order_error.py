from __future__ import annotations

import pytest

from src.agent.exceptions.conversation_order_error import ConversationOrderError


class TestConversationOrderError:
    def test_can_be_instantiated(self) -> None:
        err = ConversationOrderError("wrong order")
        assert str(err) == "wrong order"

    def test_is_exception_subclass(self) -> None:
        assert issubclass(ConversationOrderError, Exception)

    def test_can_be_raised_and_caught(self) -> None:
        with pytest.raises(ConversationOrderError):
            raise ConversationOrderError("order error")
