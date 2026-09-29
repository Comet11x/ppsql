# SPDX-FileCopyrightText: 2026-present Comet11x <comet11x@protonmail.com>
#
# SPDX-License-Identifier: MIT

import os
from collections.abc import Generator

from .logger import Logger
from .scope import VariableScope


class Line:
    """Line provides a line of SQL file"""

    def __init__(self, *, number: int, content: str, ctx: "Context"):
        self.__ctx = ctx
        self.__number = number
        self.__content = content

    def __repr__(self) -> str:
        return self.__content

    def __str__(self) -> str:
        return self.__content

    @property
    def number(self) -> int:
        """number of the line"""
        return self.__number

    @property
    def content(self) -> str:
        """content of the line"""
        return self.__content

    @content.setter
    def content(self, content: str):
        self.__ctx.replace_current_line(content)
        self.__content = content

    @property
    def file(self) -> str:
        """Getter of a file"""
        return self.__ctx.file_path


class Context(Logger):
    """Context provides context of a file which is being preprocessed"""

    FILES: set[str] = set()

    def __init__(
        self,
        *,
        file_path: str,
        content: str,
        variables: dict[str, str] | None = None,
    ):
        super().__init__(f"context:{file_path}")
        self.__file_path = file_path
        self.__lines = content.split("\n")
        variables = {} if variables is None else variables
        self.variables = VariableScope(file_path, **variables)
        self.__index = 0
        self.__generator: Generator[Line, None, None] | None = None

    @property
    def content(self):
        """this getter returns the content"""
        return "\n".join(list(filter(lambda line: line, self.__lines)))

    @property
    def dirname(self) -> str:
        """this getter returns directory name"""
        return os.path.dirname(self.__file_path)

    @property
    def filename(self) -> str:
        """this getter returns file name"""
        return os.path.basename(self.__file_path)

    @property
    def file_path(self) -> str:
        """this getter returns file path"""
        return self.__file_path

    @property
    def current_line_number(self) -> int:
        """this getter returns current number of line"""
        return self.__index

    @property
    def current_line(self) -> str:
        """Getter of a current line"""
        return self.__lines[self.__index]

    def replace_current_line(self, line: str):
        """Replaces a current line"""
        self.__lines[self.__index] = line

    def include_lines(self, lines: list[str]):
        """Includes a block of lines"""
        self.__lines = [
            *self.__lines[: self.__index],
            *lines,
            *self.__lines[self.__index :],
        ]

    def __str__(self) -> str:
        return self.content

    def __repr__(self) -> str:
        return self.content

    def __iter__(self) -> "Context":
        self.__index = 0
        return self

    def __next__(self) -> Line:
        if self.__index < len(self.__lines):
            content = self.current_line
            self.__index += 1
            return Line(number=self.__index - 1, content=content, ctx=self)
        else:
            self.__index = 0
            raise StopIteration()

    def __create_generator(self) -> Generator[Line, None, None]:
        while self.__index < len(self.__lines):
            yield Line(number=self.__index, content=self.current_line, ctx=self)
            self.__index += 1

    def walk(self) -> Generator[Line, None, None]:
        """Creates a generator which traverse lines of a file"""
        if self.__generator is None:
            self.__generator = self.__create_generator()
        return self.__generator
