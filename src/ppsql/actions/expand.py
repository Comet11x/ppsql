# SPDX-FileCopyrightText: 2026-present Comet11x <comet11x@protonmail.com>
#
# SPDX-License-Identifier: MIT

import re
import sys
from abc import ABC, abstractmethod

from ..context import Context, Line
from .base import BaseAction


class ReadValueFromVariableAction(BaseAction):
    """ReadValueFromVariableAction replaces variables by their values"""

    REGEXP = re.compile(r"^.*((\$[A-Za-z]\w*)|(\$\{[A-Za-z]\w*\})).*")

    class ParseError(Exception):
        def __init__(self):
            super().__init__("parse line error")

    class UndefVarError(Exception):
        def __init__(self, name):
            super().__init__(f"variable '{name}' undefined")

    class FSM:
        def __init__(self, line: Line, ctx: Context):
            self.ctx = ctx
            self.acc = ReadValueFromVariableAction.Accumulator()
            self.stream = ReadValueFromVariableAction.Stream(str(line))
            fsm = self
            self.FREE_STATE = ReadValueFromVariableAction.FreeState(fsm)
            self.START_OF_VAR_STATE = ReadValueFromVariableAction.StartOfVarState(fsm)
            self.BACK_SLASH = ReadValueFromVariableAction.BackSlashState(fsm)
            self.VAR_STATE = ReadValueFromVariableAction.VarState(fsm)
            self.VAR_BLOCK_STATE = ReadValueFromVariableAction.VarBlockState(fsm)
            self.STOP_STATE = ReadValueFromVariableAction.StopState(fsm)
            self.state: ReadValueFromVariableAction.BaseState = self.FREE_STATE

        def is_ready(self) -> bool:
            return self.state == self.STOP_STATE

        def next(self):
            self.state.next()

    class Accumulator(list):
        def __str__(self):
            if len(self) > 2 and self[0][1] == "$" and self[1][1] == "{":
                data = self[2:-1]
            elif len(self) > 2 and self[0][1] == "$" and self[1][1] != "{":
                data = self[1:]
            else:
                data = self[:]
            return "".join([elem[1] for elem in data])

        def __repr__(self) -> str:
            return str(self)

        def boundaries(self) -> tuple[int, int]:
            return (self[0][0], self[-1][0] + 1)

    class Stream:
        def __init__(self, line: str):
            self.__line = list(line)
            self.__index = 0
            self.start_index = 0
            self.stop_index = 0

        def __len__(self) -> int:
            return len(self.__line)

        def __iter__(self):
            self.__index = 0
            return self

        def __next__(self):
            val = self.next()
            if not bool(val):
                raise StopIteration()
            return val

        def __repr__(self) -> str:
            return str(self)

        def __str__(self) -> str:
            return "".join(self.__line)

        def next(self) -> str:
            val = ""
            if self.__index < len(self.__line):
                val = self.__line[self.__index]
                self.__index += 1
            return val

        def next_item(self) -> tuple[int, str]:
            return (self.__index, self.next())

        def prev(self) -> str:
            if self.__index > len(self.__line):
                self.__index = len(self.__line)
            if self.__index:
                self.__index -= 1
            return self.__line[self.__index]

        def current(self) -> str:
            return self.__line[self.__index]

        def current_item(self) -> tuple[int, str]:
            return (self.__index, self.__line[self.__index])

        def items(self) -> tuple[tuple[int, str], ...]:
            return tuple(enumerate(self.__line))

        def tell(self) -> int:
            return self.__index

        def getvalue(self) -> str:
            return "".join(self.__line)

        def cut(self, start: int, stop: int):
            if not 0 <= start < len(self.__line) or stop < 0 or stop > len(self.__line):
                raise IndexError("index out of range")
            if start <= self.__index < stop:
                self.__index = start - 1 if start else 0
            elif self.__index >= stop:
                self.__index -= stop - start - 1
            line = self.__line[0:start]
            if stop < len(self.__line):
                line.extend(self.__line[stop:])
            self.__line = line

        def seek(self, i: int):
            if i < 0 and len(self.__line) + i >= 0:
                self.__index = len(self.__line) + i
            elif i >= 0 and i < len(self.__line):
                self.__index = i

        def write(self, text: str):
            for symbol in text:
                if self.__index < len(self.__line):
                    self.__line[self.__index] = symbol

        def erase(self):
            if self.__index < len(self.__line):
                self.__line[self.__index] = ""
                self.__index += 1

        def insert(self, text: str):
            data = list(text)
            if self.__index == len(self.__line):
                self.__line.extend(data)
                self.__index = len(self.__line)
            else:
                sequence = [*self.__line[0 : self.__index], *data]
                self.__line = [*sequence, *self.__line[self.__index :]]
                self.__index = len(sequence) - 1

        def read(self, count: int = -1):
            if count < 0:
                count = len(self.__line)
            out = []
            if self.__index < len(self.__line):
                if self.__index + count < len(self.__line):
                    out = self.__line[self.__index : self.__index + count]
                    self.__index += count
                else:
                    out = self.__line[self.__index :]
                    self.__index = len(self.__line)
            return "".join(out)

    class BaseState(ABC):
        def __init__(self, fsm: "ReadValueFromVariableAction.FSM"):
            self.fsm = fsm

        @abstractmethod
        def next(self):
            pass

        def set_value(self, value, count=2):
            self.fsm.stream.cut(*self.fsm.acc.boundaries())
            for _ in range(count):
                self.fsm.stream.prev()
            self.fsm.stream.insert(value)
            self.fsm.stream.next()
            self.fsm.acc.clear()

    class FreeState(BaseState):
        def next(self):
            item = self.fsm.stream.next_item()
            if item[1] == "$":
                self.fsm.acc.append(item)
                self.fsm.state = self.fsm.START_OF_VAR_STATE
            elif item[1] == "\\":
                self.fsm.state = self.fsm.BACK_SLASH
            elif item[1] == "":
                self.fsm.state = self.fsm.STOP_STATE

    class StartOfVarState(BaseState):
        REGEXP = re.compile("^[a-z]$", re.IGNORECASE)

        def next(self):
            item = self.fsm.stream.next_item()
            if item[1] == "{":
                self.fsm.acc.append(item)
                self.fsm.state = self.fsm.VAR_BLOCK_STATE
            elif item[1] == "$":
                self.fsm.acc.pop()
                self.fsm.acc.append(item)
            elif ReadValueFromVariableAction.StartOfVarState.REGEXP.match(item[1]):
                self.fsm.acc.append(item)
                self.fsm.state = self.fsm.VAR_STATE
            else:
                raise ReadValueFromVariableAction.ParseError()

    class BackSlashState(BaseState):
        REGEXP = re.compile(".*")

        def next(self):
            item = self.fsm.stream.next_item()
            if item[1] != "":
                if item[1] == "$":
                    self.fsm.stream.prev()
                    self.fsm.stream.prev()
                    self.fsm.stream.erase()
                    self.fsm.stream.next()
                self.fsm.state = self.fsm.FREE_STATE
            else:
                raise ReadValueFromVariableAction.ParseError()

    class VarState(BaseState):
        REGEXP = re.compile("^[0-9a-z_]$", re.IGNORECASE)

        def next(self):
            item = self.fsm.stream.next_item()
            if item[1] in [" ", ".", "(", ")", "", ";"]:
                var_name = str(self.fsm.acc)
                value = self.fsm.ctx.variables.get(var_name)
                if value is None:
                    raise ReadValueFromVariableAction.UndefVarError(var_name)
                self.set_value(value, 0 if item[1] == "" else 2)
                if item[1] == "":
                    self.fsm.state = self.fsm.STOP_STATE
                else:
                    self.fsm.state = self.fsm.FREE_STATE
            elif ReadValueFromVariableAction.VarState.REGEXP.match(item[1]):
                self.fsm.acc.append(item)
            else:
                raise ReadValueFromVariableAction.ParseError()

    class VarBlockState(BaseState):
        REGEXP = re.compile("^[0-9a-z_]$", re.IGNORECASE)

        def next(self):
            item = self.fsm.stream.next_item()
            if item[1] == "}":
                self.fsm.acc.append(item)
                var_name = str(self.fsm.acc)
                value = self.fsm.ctx.variables.get(var_name)
                if value is None:
                    raise ReadValueFromVariableAction.UndefVarError(var_name)
                self.set_value(value, 1)
                self.fsm.state = self.fsm.FREE_STATE
            elif ReadValueFromVariableAction.VarState.REGEXP.match(item[1]):
                self.fsm.acc.append(item)
            else:
                raise ReadValueFromVariableAction.ParseError()

    class StopState(BaseState):
        def next(self):
            self.fsm.state = self.fsm.STOP_STATE

    def __call__(self, line: Line, ctx: Context):
        if ReadValueFromVariableAction.REGEXP.match(str(line)):
            try:
                fsm = ReadValueFromVariableAction.FSM(line, ctx)
                while not fsm.is_ready():
                    fsm.next()
                fsm.stream.seek(0)
                line.content = fsm.stream.read()
            except Exception as err:
                sys.stderr.write(
                    f"""\
Compile error: {err}
    file:
        {line.file}
    line {line.number}:
        {line.content}
"""
                )
                exit(1)
