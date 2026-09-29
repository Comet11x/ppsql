# SPDX-FileCopyrightText: 2026-present Comet11x <comet11x@protonmail.com>
#
# SPDX-License-Identifier: MIT

import os

import pytest

from ppsql import VariableScope, Writer
from ppsql.cli import CLIArgumentsReader, load_env, load_password, main


def test_arguments_are_parsed(sql_project):
    entry = sql_project("main.sql", "select 1;\n")
    args = CLIArgumentsReader(["-i", entry, "-s", "/tmp", "-o", "/tmp/out.sql"])
    assert args.entry == entry
    assert args.source == "/tmp"
    assert args.out == "/tmp/out.sql"
    assert args.arguments.debug is False


def test_a_missing_entry_point_stops_the_cli():
    with pytest.raises(SystemExit):
        CLIArgumentsReader(["-i", "does-not-exist.sql"])


def test_a_missing_source_directory_stops_the_cli(sql_project):
    entry = sql_project("main.sql", "select 1;\n")
    with pytest.raises(SystemExit):
        CLIArgumentsReader(["-i", entry, "-s", "does-not-exist"])


def test_a_missing_output_directory_stops_the_cli(sql_project):
    entry = sql_project("main.sql", "select 1;\n")
    with pytest.raises(SystemExit):
        CLIArgumentsReader(["-i", entry, "-o", "does-not-exist/out.sql"])


def test_load_env_reads_a_dot_env_file(tmp_path):
    (tmp_path / ".env").write_text("# comment\nexport FIRST=1\nSECOND=2\n", encoding="utf-8")
    load_env(str(tmp_path))
    assert VariableScope.global_get("FIRST") == "1"
    assert VariableScope.global_get("SECOND") == "2"


def test_load_password_reads_a_credentials_file(tmp_path):
    (tmp_path / ".password").write_text("db:user:secret\n", encoding="utf-8")
    load_password([str(tmp_path)])
    assert VariableScope.global_get("db_name") == "user"
    assert VariableScope.global_get("db_password") == "secret"


def test_main_writes_the_output_file(sql_project, tmp_path):
    entry = sql_project("main.sql", "@set name = world\nselect ${name};\n")
    out = tmp_path / "out.sql"
    main(["-i", entry, "-o", str(out), "-e", str(tmp_path), "-c", str(tmp_path)])
    assert out.read_text(encoding="utf-8") == "select world;"


def test_main_expands_environment_variables(sql_project, tmp_path):
    (tmp_path / ".env").write_text("GREETING=hi\n", encoding="utf-8")
    entry = sql_project("main.sql", "select ${GREETING};\n")
    out = tmp_path / "out.sql"
    main(["-i", entry, "-o", str(out), "-e", str(tmp_path), "-c", str(tmp_path)])
    assert out.read_text(encoding="utf-8") == "select hi;"


def test_main_accepts_a_relative_output_path(sql_project, tmp_path):
    entry = sql_project("main.sql", "select 1;\n")
    os.chdir(tmp_path)
    main(["-i", entry, "-o", "out.sql"])
    assert (tmp_path / "out.sql").read_text(encoding="utf-8") == "select 1;"


def test_writer_creates_and_fills_a_file(tmp_path):
    out = tmp_path / "out.sql"
    writer = Writer(str(out))
    writer("select 1;")
    writer("select 2;")
    assert out.read_text(encoding="utf-8") == "select 1;select 2;"


def test_writer_rejects_a_missing_directory(tmp_path):
    with pytest.raises(Writer.OutDirectoryNotFoundError):
        Writer(str(tmp_path / "nope" / "out.sql"))
