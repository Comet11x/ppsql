# SPDX-FileCopyrightText: 2026-present Comet11x <comet11x@protonmail.com>
#
# SPDX-License-Identifier: MIT

import sys
from pathlib import Path

from .context import Context
from .logger import Logger


class Loader(Logger):
    """Loader loads a content from sql file"""

    def __init__(self, file_path: Path):
        super().__init__("loader")
        self.file_path = file_path

        if self.file_path in Context.FILES:
            self.logger.critical(f"this file '{self.file_path}' has been already included")
            sys.exit(1)

        if not file_path.is_file():
            self.logger.critical(f"File not found {file_path}")
            sys.exit(1)

    def __call__(self) -> Context:
        with open(self.file_path, encoding="utf-8") as file:
            data = file.read()
        return Context(file_path=self.file_path, content=data)
