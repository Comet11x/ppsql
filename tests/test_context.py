# SPDX-FileCopyrightText: 2026-present Comet11x <comet11x@protonmail.com>
#
# SPDX-License-Identifier: MIT

from pathlib import Path

import pytest

from ppsql import Context, Line


@pytest.fixture
def ctx():
    return Context(file_path=Path("/tmp/example.sql"), content="first\nsecond\nthird")


def test_content_joins_non_empty_lines(ctx):
    assert ctx.content == "first\nsecond\nthird"


def test_file_properties(ctx):
    assert ctx.file_path == "/tmp/example.sql"
    assert ctx.filename == "example.sql"
    assert ctx.dirname == "/tmp"


def test_str_returns_content(ctx):
    assert str(ctx) == ctx.content
    assert repr(ctx) == ctx.content


def test_walk_yields_every_line(ctx):
    lines = list(ctx.walk())
    assert [line.content for line in lines] == ["first", "second", "third"]
    assert [line.number for line in lines] == [0, 1, 2]


def test_walk_returns_the_same_generator(ctx):
    assert ctx.walk() is ctx.walk()


def test_iteration(ctx):
    assert [line.content for line in ctx] == ["first", "second", "third"]


def test_a_trailing_newline_produces_an_empty_line():
    ctx = Context(file_path=Path("/tmp/example.sql"), content="first\n")
    assert [line.content for line in ctx.walk()] == ["first", ""]


def test_line_file_points_to_the_context(ctx):
    line = next(iter(ctx))
    assert line.file == "/tmp/example.sql"


def test_a_changed_line_is_written_back(ctx):
    for line in ctx.walk():
        if line.content == "second":
            line.content = "changed"
    assert ctx.content == "first\nchanged\nthird"


def test_current_line(ctx):
    iter(ctx)
    assert ctx.current_line_number == 0
    assert ctx.current_line == "first"
    ctx.replace_current_line("replaced")
    assert ctx.current_line == "replaced"


def test_include_lines(ctx):
    iter(ctx)
    ctx.include_lines(["inserted"])
    assert ctx.content == "inserted\nfirst\nsecond\nthird"


def test_a_line_is_a_string(ctx):
    line = Line(number=0, content="select 1;", ctx=ctx)
    assert str(line) == "select 1;"
    assert f"{line}" == "select 1;"


def test_variables_of_a_context_are_isolated():
    first = Context(file_path=Path("/tmp/first.sql"), content="", variables={"key": "1"})
    second = Context(file_path=Path("/tmp/second.sql"), content="")
    assert first.variables.get("key") == "1"
    assert second.variables.get("key") is None
