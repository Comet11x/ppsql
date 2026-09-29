# SPDX-FileCopyrightText: 2026-present Comet11x <comet11x@protonmail.com>
#
# SPDX-License-Identifier: MIT

import os
import sys
from typing import Any

from .actions import (
    Action,
    CommentLineAction,
    IncludeFileAction,
    ReadValueFromVariableAction,
    SetVariableAction,
    UnsetVariableAction,
)
from .context import Context, Line
from .loader import Loader
from .logger import Logger


class Builder(Logger):
    """Builder preprocesses an entry file and returns its content"""

    files: set[str] = set()

    translators: list[Action] = [
        CommentLineAction(),
        ReadValueFromVariableAction(),
        IncludeFileAction(),
        SetVariableAction(),
        UnsetVariableAction(),
    ]

    def __init__(
        self,
        *,
        entry: str,
        variables: dict[str, Any] | None = None,
    ):
        entry = os.path.abspath(os.path.normpath(entry))
        Logger.__init__(self, f"builder:{entry}")
        if entry in Builder.files:
            self.logger.critical(f"recursive include file: {entry}")
            sys.exit(1)
        else:
            Builder.files.add(os.path.abspath(entry))
        self.__entry = entry
        self.__variables = variables if isinstance(variables, dict) else {}

    def __make_context(self) -> Context:
        loader = Loader(self.__entry)
        ctx = loader()
        ctx.variables.update(self.__variables)
        return ctx

    def __translate(self, line: Line, ctx: Context):
        for tr in Builder.translators:
            tr(line, ctx)

    def build(self) -> str:
        ctx = self.__make_context()
        for line in ctx.walk():
            self.__translate(line, ctx)
        return ctx.content
