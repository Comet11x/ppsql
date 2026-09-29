# SPDX-FileCopyrightText: 2026-present Comet11x <comet11x@protonmail.com>
#
# SPDX-License-Identifier: MIT

import re

from .actions import Action
from .context import Context, Line


class Translator:
    """Translator applies an action to the lines which match a regexp"""

    def __init__(self, *, regex: re.Pattern, action: Action):
        self.__pattern = regex
        self.__action = action

    def __call__(self, line: Line, ctx: Context, *args, **kwargs) -> str:
        new_line = f"{line}"
        if self.__pattern.match(line):
            new_line = self.__action(line, ctx, *args, **kwargs)
        return new_line
