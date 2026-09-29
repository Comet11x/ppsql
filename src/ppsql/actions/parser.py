# SPDX-FileCopyrightText: 2026-present Comet11x <comet11x@protonmail.com>
#
# SPDX-License-Identifier: MIT

import re

from ..context import Line


class StatementParser:
    """StatementParser parses preprocessor statements"""

    REGEXP = re.compile(r"^@(un)?set\s+global\s+\w+\s*=\s*.*;?$")

    def set(self, line: Line) -> list[str]:
        return self(line, "@set")

    def unset(self, line) -> list[str]:
        return self(line, "@unset")

    def include(self, line) -> str:
        return self.__prepare_line(line, "@include")

    def __prepare_line(self, line: Line, tag: str) -> str:
        return str(line).replace(";", "").replace(tag, "").strip()

    def __call__(self, line: Line, tag: str = "@set"):
        vec: list[str] = self.__prepare_line(line, tag).split("=")
        if len(vec) > 1:
            if StatementParser.REGEXP.match(str(line)):
                vec[0] = vec[0].split("global")[-1]
                vec.append("global")
            vec = [elem.strip() for elem in vec]
        else:
            vec = []
        return vec
