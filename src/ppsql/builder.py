# SPDX-FileCopyrightText: 2026-present Comet11x <comet11x@protonmail.com>
#
# SPDX-License-Identifier: MIT

import os
import sys
from pathlib import Path
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

    files: set[str | Path] = set()

    INDEX_FILE = "index.sql"

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
        entrypoint: str | Path,
        variables: dict[str, Any] | None = None,
    ):
        entrypoint = Builder.__normile_path(entrypoint)
        Logger.__init__(self, f"builder:{entrypoint}")

        if entrypoint in Builder.files:
            self.logger.critical(f"recursive include file: {entrypoint}")
            sys.exit(1)
        else:
            Builder.files.add(entrypoint)
        self.__entrypoint = entrypoint
        self.__variables = variables if isinstance(variables, dict) else {}

    @staticmethod
    def __normile_path(path: Path | str) -> Path:
        entrypoint = Path(os.path.normpath(path)).absolute()
        if entrypoint.is_dir() and Builder.INDEX_FILE in os.listdir(entrypoint):
            entrypoint = entrypoint / Builder.INDEX_FILE

        return entrypoint

    def __make_context(self) -> Context:
        loader = Loader(self.__entrypoint)
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
