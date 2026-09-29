# SPDX-FileCopyrightText: 2026-present Comet11x <comet11x@protonmail.com>
#
# SPDX-License-Identifier: MIT

import os
import re

from ..context import Context, Line
from .base import BaseAction
from .parser import StatementParser


class RemoveLineAction:
    """RemoveLineAction removes a line from a file"""

    def __call__(self, line, ctx: Context):
        line.content = ""


class CommentLineAction(BaseAction):
    """CommentLineAction removes SQL comments"""

    REGEXP = re.compile(r"^\-{2}.*$")

    def __call__(self, line: Line, ctx: Context):
        if CommentLineAction.REGEXP.match(str(line).strip()):
            RemoveLineAction()(line, ctx)


class SetVariableAction(BaseAction):
    """SetVariableAction handles an `@set` statement"""

    REGEXP = re.compile(r"^\s*@set\s+(global\s+)?\w+\s*=\s*.*;?$")

    def __call__(self, line: Line, ctx: Context):
        if self.pattern.match(str(line)):
            vec = StatementParser().set(line)
            if len(vec) > 1:
                key, value = vec[:2]
                fn = ctx.variables.global_set if len(vec) == 3 else ctx.variables.set
                fn(key, value)
                RemoveLineAction()(line, ctx)


class UnsetVariableAction(BaseAction):
    """UnsetVariableAction handles an `@unset` statement"""

    REGEXP = re.compile(r"^\s*@unset\s+(global\s+)?\w+\s*=\s*.*;?$")

    def __call__(self, line: Line, ctx: Context):
        if self.pattern.match(str(line)):
            vec = StatementParser().unset(line)
            if len(vec) > 1:
                key, value = vec[:2]
                fn = ctx.variables.global_unset if len(vec) else ctx.variables.unset
                fn(key)
                RemoveLineAction()(line, ctx)


class IncludeFileAction(BaseAction):
    """IncludeFileAction handles an `@include` statement"""

    REGEXP = re.compile(r"^\s*@include\s+[0-9A-Za-z-/._]+\s*;?\s*$")

    def __call__(self, line: Line, ctx: Context):
        if self.pattern.match(str(line)):
            from ..builder import Builder

            file_path = StatementParser().include(line)
            alternative_path = os.path.join(ctx.dirname, file_path)

            # get the target of fs
            if not os.path.isdir(file_path) and not os.path.isfile(file_path):
                file_path = alternative_path

            if os.path.isdir(file_path):
                _, _, files = next(os.walk(file_path))
                if "index.sql" in files:
                    file_path = f"{file_path}/index.sql"

            builder = Builder(entry=file_path, variables=ctx.variables)
            line.content = builder.build()
