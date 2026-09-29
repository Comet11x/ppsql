# SPDX-FileCopyrightText: 2026-present Comet11x <comet11x@protonmail.com>
#
# SPDX-License-Identifier: MIT

"""ppsql preprocesses SQL files: variables, includes and comments"""

from .__about__ import __version__
from .actions import (
    Action,
    BaseAction,
    CommentLineAction,
    IncludeFileAction,
    ReadValueFromVariableAction,
    RemoveLineAction,
    SetVariableAction,
    StatementParser,
    UnsetVariableAction,
)
from .builder import Builder
from .cli import CLIArgumentsReader, load_env, load_password, main
from .context import Context, Line
from .loader import Loader
from .logger import Logger
from .scope import VariableScope
from .translator import Translator
from .writer import Writer

__all__ = [
    "__version__",
    "Logger",
    "VariableScope",
    "Line",
    "Context",
    "Loader",
    "Translator",
    "Action",
    "BaseAction",
    "StatementParser",
    "RemoveLineAction",
    "CommentLineAction",
    "SetVariableAction",
    "UnsetVariableAction",
    "IncludeFileAction",
    "ReadValueFromVariableAction",
    "Writer",
    "Builder",
    "CLIArgumentsReader",
    "load_env",
    "load_password",
    "main",
]
