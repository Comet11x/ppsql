# SPDX-FileCopyrightText: 2026-present Comet11x <comet11x@protonmail.com>
#
# SPDX-License-Identifier: MIT

import os
from typing import Any

from .logger import Logger


class VariableScope(dict, Logger):
    """
    Variable scope type
    """

    __GLOBAL: dict[str, str | None] = {**os.environ}

    def __init__(self, name, **kwargs):
        dict.__init__(self, kwargs)
        Logger.__init__(self, f"scope:{name}")

    def set(self, key: str, value: Any):
        """
        function
        """
        if isinstance(value, str) and value[0] == "$":
            value = super().get(value, VariableScope.__GLOBAL.get(value, value))
        self[key] = value

    def unset(self, key: str):
        """unset a variable in a local scope"""
        self[key] = None

    def get(self, key: str, default: Any = None) -> Any:
        """set variable"""
        return super().get(key, VariableScope.__GLOBAL.get(key, default))

    def extend(self, variables: "VariableScope") -> "VariableScope":
        self.update(variables)
        return self

    @classmethod
    def global_get(cls, key: str) -> Any:
        return cls.__GLOBAL.get(key)

    @classmethod
    def global_set(cls, key: str, value: Any):
        """set a variable into the global space"""
        cls.__GLOBAL[key] = value

    @classmethod
    def global_unset(cls, key: str):
        """unset a variable from the global space"""
        cls.__GLOBAL[key] = None

    @classmethod
    def clear_globals(cls):
        """removes every variable from the global space"""
        cls.__GLOBAL.clear()
