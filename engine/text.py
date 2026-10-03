"""Text chunking for Telegram's 4096-char message limit."""

TELEGRAM_LIMIT = 4096


def split_text(text: str, limit: int = TELEGRAM_LIMIT) -> list:
    """Split on a line boundary if possible, else a word boundary, else hard cut."""
    if len(text) <= limit:
        return [text]

    chunks = []
    remaining = text
    while len(remaining) > limit:
        window = remaining[:limit]

        cut = window.rfind("\n")
        if cut == -1:
            cut = window.rfind(" ")
        if cut == -1 or cut == 0:
            cut = limit

        chunks.append(remaining[:cut])
        remaining = remaining[cut:].lstrip("\n ")

    if remaining:
        chunks.append(remaining)
    return chunks
