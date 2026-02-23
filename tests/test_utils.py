"""utils 模块单元测试"""

import tempfile
from pathlib import Path

import pytest

from resume_agent.utils import load_text, save_text


def test_save_and_load_text() -> None:
    """保存并加载文本应保持一致"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
        path = f.name
    try:
        content = "测试内容\n第二行"
        save_text(content, path)
        assert load_text(path) == content
    finally:
        Path(path).unlink(missing_ok=True)
