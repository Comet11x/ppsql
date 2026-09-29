# SPDX-FileCopyrightText: 2026-present Comet11x <comet11x@protonmail.com>
#
# SPDX-License-Identifier: MIT

from pathlib import Path

import pytest

from ppsql import Context, StatementParser


@pytest.fixture
def ctx():
    return Context(file_path=Path("/tmp/example.sql"), content="")


def line(ctx, content):
    ctx.replace_current_line(content)
    return next(iter(ctx))


def test_set_statement(ctx):
    assert StatementParser().set(line(ctx, "@set name = world")) == ["name", "world"]


def test_set_statement_with_semicolon(ctx):
    assert StatementParser().set(line(ctx, "@set name = world;")) == ["name", "world"]


def test_set_global_statement(ctx):
    vec = StatementParser().set(line(ctx, "@set global name = world"))
    assert vec[:2] == ["name", "world"]
    assert vec[2] == "global"


def test_unset_statement(ctx):
    assert StatementParser().unset(line(ctx, "@unset name =")) == ["name", ""]


def test_include_statement(ctx):
    assert StatementParser().include(line(ctx, "@include part.sql;")) == "part.sql"


def test_statement_without_a_value(ctx):
    assert StatementParser().set(line(ctx, "@set name")) == []
