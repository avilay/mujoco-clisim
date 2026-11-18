import re
from typing import Protocol

import mujoco
import numpy as np
from pyfun import Iter, Maybe, Some, maybe, wrap_exc

toint = wrap_exc(int, ValueError)
tofloat = wrap_exc(float, ValueError)


class Command(Protocol):
    def is_match(self, cmd: str) -> bool: ...
    def run(self) -> None: ...
    def help(self) -> str: ...


class Unknown(Command):
    def help(self) -> str:
        return ""

    def is_match(self, cmd: str) -> bool:
        return True

    def run(self) -> None:
        print("Unknown command.")


class GetData(Command):
    def __init__(self, data: mujoco.MjData, attr: str, cmd: str | None = None) -> None:
        self._data = data
        self._attr = attr
        self._cmd = cmd or self._attr

    def help(self) -> str:
        return self._cmd

    def is_match(self, cmd: str) -> bool:
        return self._cmd == cmd

    def run(self) -> None:
        print(getattr(self._data, self._attr))


class GetDataIdx(Command):
    def __init__(self, data: mujoco.MjData, attr: str, cmd: str | None = None) -> None:
        self._data = data
        self._attr = attr
        self._cmd = cmd or self._attr
        self._idx: Maybe[int] = maybe(None)
        self._len: int = len(getattr(data, attr))

    def help(self) -> str:
        return f"{self._cmd}[idx]"

    def is_match(self, cmd: str) -> bool:
        self._idx = (
            maybe(re.match(rf"{self._cmd}\[(\d+)\]", cmd))
            .map(lambda match: match.group(1))
            .bind(toint)
        )
        return isinstance(self._idx, Some)

    def run(self) -> None:
        self._idx.filter(lambda idx: idx < self._len).map(
            lambda idx: getattr(self._data, self._attr)[idx]
        ).map(lambda val: print(f"{val:.5f}"))
        self._idx = maybe(None)


class SetData(Command):
    def __init__(self, data: mujoco.MjData, attr: str, cmd: str | None = None) -> None:
        self._data = data
        self._attr = attr
        self._cmd = cmd or self._attr
        self._newvals: Maybe[str] = maybe(None)

    def help(self) -> str:
        return f"set {self._cmd} <val>"

    def _writeattr(self, newvals: list[float]) -> None:
        if newvals:
            setattr(self._data, self._attr, np.array(newvals))

    def is_match(self, cmd: str) -> bool:
        self._newvals = maybe(re.match(rf"set {self._cmd}\s+(.*)", cmd)).map(
            lambda match: match.group(1)
        )
        return isinstance(self._newvals, Some)

    def run(self) -> None:
        self._newvals.map(str2ary).map(self._writeattr)
        self._newvals = maybe(None)


class SetDataIdx(Command):
    def __init__(self, data: mujoco.MjData, attr: str, cmd: str | None = None) -> None:
        self._data = data
        self._attr = attr
        self._cmd = cmd or self._attr
        self._idx: Maybe[int] = maybe(None)
        self._newval: Maybe[str] = maybe(None)
        self._len = len(getattr(data, attr))

    def help(self) -> str:
        return f"set {self._cmd}[idx] <val>"

    def is_match(self, cmd: str) -> bool:
        maybe_match = maybe(re.match(rf"set {self._cmd}\[(\d+)\]\s+(\S+)", cmd))
        self._idx = maybe_match.map(lambda match: match.group(1)).bind(toint)
        self._newval = maybe_match.map(lambda match: match.group(2))
        return isinstance(self._idx, Some) and isinstance(self._newval, Some)

    def run(self) -> None:
        maybe_newval = self._newval.bind(tonum)
        match self._idx, maybe_newval:
            case Some(idx), Some(newval) if idx < self._len:
                if idx < self._len:
                    getattr(self._data, self._attr)[idx] = newval
            case _:
                print("Syntax error")
        self._idx = maybe(None)
        self._newval = maybe(None)


def tonum(s: str) -> Maybe[float]:
    sign = 1
    if s.startswith("-"):
        sign = -1
        s = s[1:]
    if s.startswith("pi/") or s.startswith("π/"):
        return (
            toint(s.split("/")[1])
            .map(lambda denom: np.pi / denom)
            .map(lambda num: sign * num)
        )
    else:
        return tofloat(s).map(lambda f: sign * f)


def str2ary(strnums: str) -> list[float]:
    """Converts a space-separated line of numbers to a numpy array of floats
    The numbers can be separated by any number of spaces. Numbers of the form
    pi/3 or π/3 are also converted to their floating point equivalents.
    """
    return Iter(strnums.strip().split()).filter_map(tonum).to_list()
