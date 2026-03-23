"""Tests for history.py — chat history sliding window."""

from travel_assistant.history import trim_chat_history, sanitize_for_history


class TestTrimChatHistory:
    def test_short_history_unchanged(self):
        history = [("user", "hi"), ("assistant", "hello")]
        assert trim_chat_history(history, max_pairs=20) == history

    def test_trims_to_max_pairs(self):
        # 5 pairs = 10 messages; trim to last 2 pairs = 4 messages
        history = [(role, f"msg{i}") for i in range(10)
                   for role in ("user", "assistant")][:10]
        result = trim_chat_history(history, max_pairs=2)
        assert len(result) == 4

    def test_returns_most_recent_messages(self):
        history = [
            ("user", "first"), ("assistant", "first reply"),
            ("user", "second"), ("assistant", "second reply"),
            ("user", "third"), ("assistant", "third reply"),
        ]
        result = trim_chat_history(history, max_pairs=1)
        assert result == [("user", "third"), ("assistant", "third reply")]

    def test_does_not_mutate_original(self):
        history = [("user", "a"), ("assistant", "b")] * 25
        original_len = len(history)
        trim_chat_history(history, max_pairs=5)
        assert len(history) == original_len  # original unchanged

    def test_empty_history(self):
        assert trim_chat_history([], max_pairs=10) == []


class TestSanitizeForHistory:
    def test_strips_control_characters(self):
        result = sanitize_for_history("hello\x00world")
        assert "\x00" not in result

    def test_normal_text_preserved(self):
        result = sanitize_for_history("Book a hotel in Paris")
        assert result == "Book a hotel in Paris"
