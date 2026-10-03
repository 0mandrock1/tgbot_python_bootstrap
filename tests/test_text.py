from engine.text import split_text


def test_short_text_not_split():
    assert split_text("hello") == ["hello"]


def test_splits_on_line_boundary():
    text = ("a" * 4000) + "\n" + ("b" * 200)
    chunks = split_text(text, limit=4096)
    assert len(chunks) == 2
    assert "".join(chunks).replace("\n", "") != ""
    assert all(len(c) <= 4096 for c in chunks)


def test_splits_long_text_over_limit():
    text = "word " * 2000  # far over 4096 chars
    chunks = split_text(text, limit=4096)
    assert len(chunks) > 1
    assert all(len(c) <= 4096 for c in chunks)
    assert "".join(chunks).replace(" ", "") == text.replace(" ", "")
