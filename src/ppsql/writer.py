# SPDX-FileCopyrightText: 2026-present Comet11x <comet11x@protonmail.com>
#
# SPDX-License-Identifier: MIT

import os


class Writer:
    """Writer writes the preprocessed content into a file"""

    class OutDirectoryNotFoundError(Exception):
        def __init__(self):
            super().__init__("out direcotry not found")

    def __init__(self, out: str):
        out = os.path.abspath(out)
        if os.path.isdir(os.path.dirname(out)):
            self.__out = out
        else:
            raise Writer.OutDirectoryNotFoundError()
        with open(self.__out, "w") as _:
            pass

    def __call__(self, content: str):
        with open(self.__out, "a") as fp:
            fp.write(content)
