# SPDX-FileCopyrightText: 2026-present Comet11x <comet11x@protonmail.com>
#
# SPDX-License-Identifier: MIT

import pytest

from ppsql import Builder, Context, VariableScope


@pytest.fixture(autouse=True)
def clean_state():
    Builder.files.clear()
    Context.FILES.clear()
    VariableScope.clear_globals()
    yield
    Builder.files.clear()
    Context.FILES.clear()
    VariableScope.clear_globals()


@pytest.fixture
def sql_project(tmp_path):
    def create(name: str, content: str) -> str:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return str(path)

    return create
