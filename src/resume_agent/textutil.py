"""单行截断（命令行展示）。"""


def one_line(text: str, max_len: int = 140) -> str:
    s = " ".join(text.split())
    if len(s) <= max_len:
        return s
    return s[: max_len - 1] + "…"
