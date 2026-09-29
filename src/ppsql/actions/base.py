# SPDX-FileCopyrightText: 2026-present Comet11x <comet11x@protonmail.com>
#
# SPDX-License-Identifier: MIT

import re
from typing import Protocol

from ..context import Context, Line


class Action(Protocol):
    """Basic action"""

    @property
    def pattern(self) -> re.Pattern:
        """Getter regexp pattern"""
        return re.compile(".*")

    def __call__(self, line: Line, ctx: Context, *args, **kwargs) -> str:
        """Interface Action"""
        return ""


class BaseAction:
    """BaseAction is a base class of every preprocessor action"""

    REGEXP = re.compile(".*")

    @property
    def pattern(self) -> re.Pattern:
        return self.__class__.REGEXP
