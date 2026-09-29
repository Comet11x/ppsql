# SPDX-FileCopyrightText: 2026-present Comet11x <comet11x@protonmail.com>
#
# SPDX-License-Identifier: MIT

import argparse
import logging
import os
import re
import sys
from pathlib import Path

from .builder import Builder
from .logger import Logger
from .scope import VariableScope
from .writer import Writer

__cwd__ = os.getcwd()
__home__ = str(Path.home())


class CLIArgumentsReader:
    """CLIArgumentsReader reads and validates command line arguments"""

    def __init__(self, argv: list[str] | None = None):
        parser = argparse.ArgumentParser(
            prog="ppsql",
            description="preprocess SQL files before using them",
        )
        parser.add_argument("-i", "--input", help="set path for an entry point", type=str)
        parser.add_argument(
            "-s",
            "--source",
            help="set path for a source directory",
            type=str,
            default=os.getcwd(),
        )
        parser.add_argument(
            "-o",
            "--out",
            help="output file",
            type=str,
            default=f"{os.getcwd()}/out.sql",
        )
        parser.add_argument(
            "-e",
            "--env",
            help="set path for env file",
            type=str,
            default=__cwd__,
        )
        parser.add_argument("-d", "--debug", help="debug mode", action="store_true")
        parser.add_argument(
            "-c", "--credential", help="credential file", type=str, default=__home__
        )
        self.__args = parser.parse_args(argv)
        self.__validate()
        Logger.get_logger(logging.DEBUG if self.__args.debug else logging.ERROR)

    def __validate(self):
        if self.entry is None or not os.path.isfile(self.entry):
            sys.stderr.write("entry point not found\n")
            sys.exit(1)
        if not os.path.isdir(self.source):
            sys.stderr.write("source directory not found\n")
            sys.exit(2)
        if not os.path.isdir(os.path.dirname(os.path.abspath(self.out))):
            sys.stderr.write("output directory not found\n")
            sys.exit(3)

    @property
    def arguments(self):
        """Getter of args"""
        return self.__args

    @property
    def entry(self) -> str:
        """Getter of an antry point"""
        return self.__args.input

    @property
    def source(self) -> str:
        """Getter of a source directory"""
        return self.__args.source

    @property
    def out(self) -> str:
        """Getter of a out file"""
        return self.__args.out

    @property
    def env(self) -> str:
        """Getter variable of environment"""
        return self.__args.env

    @property
    def credential(self) -> str:
        """Getter of a file with credentials"""
        return self.__args.credential


def load_env(path=__cwd__, divider="="):
    """Loads variables from a file or a directory into the global scope"""
    regexp = re.compile("^export.*$")
    targets = [path, os.path.join(path, ".env"), os.path.join(path, "_env")]
    content = ""
    for target in targets:
        if os.path.isfile(target):
            with open(target) as fp:
                content = fp.read()
    for line in content.split("\n"):
        line = line.strip()
        if len(line) and line[0] != "#":
            if regexp.match(line):
                line = line.split("export")[1]
            sequence = line.split(divider)
            if len(sequence) == 2:
                key = sequence[0].strip()
                value = sequence[1].strip()
                VariableScope.global_set(key, value)


def load_password(paths):
    """Loads credentials from files into the global scope"""
    for p in paths:
        credentials = [f"{p}/.password", f"{p}/_password"]
        for credential in credentials:
            if os.path.isfile(credential):
                with open(credential) as fp:
                    for line in fp.read().split("\n"):
                        try:
                            sections = line.split(":")
                            if len(sections) > 2:
                                key, name, password = sections
                                VariableScope.global_set(f"{key}_name", name)
                                VariableScope.global_set(f"{key}_password", password)
                            elif len(sections) == 2:
                                key, value = sections
                                VariableScope.global_set(f"{key}_NAME", key.lower())
                                VariableScope.global_set(f"{key}_PASSWORD", value)
                            else:
                                pass
                        except Exception:
                            pass


def main(argv: list[str] | None = None) -> None:
    """Entry point of the command line interface"""
    args = CLIArgumentsReader(argv).arguments
    load_env(args.env)
    load_password([args.credential, __cwd__, __home__])
    builder = Builder(entry=args.input)
    writer = Writer(args.out)
    writer(builder.build())
