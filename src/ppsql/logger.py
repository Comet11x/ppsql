# SPDX-FileCopyrightText: 2026-present Comet11x <comet11x@protonmail.com>
#
# SPDX-License-Identifier: MIT

import logging
from collections.abc import Callable
from typing import Any


class Logger:
    """Logger class"""

    __NAME = "jsb"
    __ctx: dict[str, logging.Logger] = {}
    __FORMAT = " ".join(
        [
            "%(asctime)s.%(msecs)03d",
            "[%(module)s] >> %(name)s",
            "[%(levelname)s] -> %(message)s",
        ]
    )

    def __init__(self, name, *, parent=None):
        if isinstance(parent, logging.Logger):
            self.__logger = parent.getChild(name)
        else:
            self.__logger = Logger.get_logger().getChild(name)

    @property
    def logger(self) -> logging.Logger:
        """property"""
        return self.__logger

    @staticmethod
    def get_logger(level=logging.ERROR) -> logging.Logger:
        """get logger"""
        if Logger.__ctx.get(Logger.__NAME) is None:
            logging.basicConfig(
                format=Logger.__FORMAT,
                datefmt="%Y-%m-%d,%H:%M:%S",
                level=level,
            )

            Logger.__ctx[Logger.__NAME] = logging.getLogger(Logger.__NAME)
        return Logger.__ctx[Logger.__NAME]

    @classmethod
    def log(cls, name: str, *, parent=None) -> Callable[[Any], Any]:
        """Prints a log message"""
        logger = Logger(name, parent=parent).logger

        def wrapper(callee: Callable[[Any], Any]) -> Callable[[Any], Any]:

            def decorator(*args, **kwargs) -> Any:
                try:
                    logger.debug(f"call `{callee}` with args: {args} and kwargs: {kwargs}")
                    res = callee(*args, **kwargs)
                    logger.debug(f"`{callee}` has returned {res}")
                    return res
                except Exception as error:
                    logger.error(error)
                    raise error

            return decorator

        return wrapper
