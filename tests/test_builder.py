# SPDX-FileCopyrightText: 2026-present Comet11x <comet11x@protonmail.com>
#
# SPDX-License-Identifier: MIT

import pytest

from ppsql import Builder, VariableScope


def build(entry, variables=None):
    return Builder(entry=entry, variables=variables).build()


def test_plain_sql_is_untouched(sql_project):
    entry = sql_project("main.sql", "select 1;\n")
    assert build(entry) == "select 1;"


def test_set_a_variable_and_expand_it(sql_project):
    entry = sql_project("main.sql", "@set name = world\nselect ${name};\n")
    assert build(entry) == "select world;"


def test_set_a_global_variable_and_expand_it(sql_project):
    entry = sql_project("main.sql", "@set global name = world\nselect ${name};\n")
    assert build(entry) == "select world;"
    assert VariableScope.global_get("name") == "world"


def test_a_statement_is_removed_from_the_output(sql_project):
    entry = sql_project("main.sql", "@set name = world\nselect 1;\n")
    assert build(entry) == "select 1;"


def test_comments_are_removed(sql_project):
    entry = sql_project("main.sql", "-- comment\nselect 1;\n   -- indented\n")
    assert build(entry) == "select 1;"


def test_a_variable_can_be_escaped(sql_project):
    entry = sql_project("main.sql", "@set name = world\nselect \\${name};\n")
    assert build(entry) == "select ${name};"


def test_several_variables_on_different_lines(sql_project):
    entry = sql_project("main.sql", "@set first = 1\n@set second = 2\nselect ${first};\n")
    assert build(entry) == "select 1;"


def test_variables_are_passed_to_the_builder(sql_project):
    entry = sql_project("main.sql", "select ${name};\n")
    assert build(entry, {"name": "world"}) == "select world;"


def test_an_undefined_variable_stops_the_build(sql_project, capsys):
    entry = sql_project("main.sql", "select ${missing};\n")
    with pytest.raises(SystemExit):
        build(entry)
    assert "variable 'missing' undefined" in capsys.readouterr().err


def test_include_a_file(sql_project):
    entry = sql_project("main.sql", "select 1;\n@include part.sql\nselect 2;\n")
    sql_project("part.sql", "select 'part';\n")
    assert build(entry) == "select 1;\nselect 'part';\nselect 2;"


def test_include_a_directory(sql_project):
    entry = sql_project("main.sql", "@include sub\n")
    sql_project("sub/index.sql", "select 'index';\n")
    assert build(entry) == "select 'index';"


def test_an_included_file_sees_the_parent_variables(sql_project):
    entry = sql_project("main.sql", "@set name = world\n@include part.sql\n")
    sql_project("part.sql", "select ${name};\n")
    assert build(entry) == "select world;"


def test_a_recursive_include_stops_the_build(sql_project):
    entry = sql_project("main.sql", "@include part.sql\n")
    sql_project("part.sql", "@include main.sql\n")
    with pytest.raises(SystemExit):
        build(entry)


def test_an_entry_point_is_registered(sql_project):
    entry = sql_project("main.sql", "select 1;\n")
    build(entry)
    assert entry in Builder.files


def test_a_missing_file_stops_the_build():
    with pytest.raises(SystemExit):
        build("does-not-exist.sql")
