#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Initial author: Bryan Hu.

@ThatXliner.

A file containing ansi escape codes for color!

See https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797#color-codes

"""

import os as _os
import shutil as _shutil
import sys as _sys
from typing import Dict, NoReturn, Optional, Tuple

try:
    import colorama  # type: ignore

    colorama.init()  # type: ignore
except ImportError:
    pass

_ansi_prefix: str = "\033["


class Interface:

    colors_dict: Dict[str, str] = {
        "red": "31",
        "green": "32",
        "yellow": "33",
        "blue": "34",
        "magenta": "35",
        "cyan": "36",
        "white": "37",
        "black": "30",
    }
    bg_dict: Dict[str, str] = {
        key: str(int(value) + 10) for key, value in colors_dict.items()
    }
    graphic_modes = {"reset": "0", "bold": "1", "dim": "2"}
    TERM_SIZE = _shutil.get_terminal_size()
    COLUMNS: int = TERM_SIZE.columns
    LINES: int = TERM_SIZE.lines

    def __init__(self, force_color: bool = False, no_color: bool = False) -> None:
        if force_color and no_color:
            raise ValueError(
                "arguments 'force_color' and 'no_color' are mutually exclusive", 1
            )
        self._print_colors: bool = force_color or (
            not no_color and _sys.stdout.isatty()
        )

    def __getattr__(self, attr: str) -> str:
        if not self._print_colors:
            return ""

        def parse_fore_back(to_parse: str) -> Tuple[str, Optional[str]]:
            string = to_parse.split("_on_")
            if len(string) == 1:
                try:
                    return self.colors_dict[string[0]], None
                except KeyError as exception:
                    raise ValueError("invalid color name") from exception

            elif len(string) == 2:
                try:
                    foreground = self.colors_dict[string[0]]
                except KeyError as exception:
                    raise ValueError("invalid color name") from exception

                try:
                    background = self.bg_dict[string[1]]
                except KeyError as exception:
                    raise ValueError("invalid color name") from exception

                return foreground, background

            raise ValueError("invalid color format: too many 'on's")

        cleaned = "".join(
            letter
            for letter in attr.strip().lower()
            if letter in "qwertyuiopasdfghjklzxcvbnm_"
        ).strip("_")
        if not (cleaned or "".join(cleaned)):
            raise AttributeError(f"invalid color format: got {cleaned}")

        mode = cleaned.split("_as_")
        if self.graphic_modes.get(cleaned):
            return _ansi_prefix + f"{self.graphic_modes[cleaned]}m"

        try:
            parsed = parse_fore_back(cleaned)
        except ValueError:
            parsed = parse_fore_back(mode[0])
        color = f"{parsed[0]};{parsed[1]}m" if parsed[1] else f"{parsed[0]}m"

        if len(mode) == 1:
            return _ansi_prefix + color

        if len(mode) == 2:
            try:
                return _ansi_prefix + f"{self.graphic_modes[mode[1]]};{color}"
            except KeyError as exception:
                raise AttributeError("invalid mode name") from exception
        assert len(mode) > 2
        raise AttributeError("invalid mode/color name")

    def info(self, msg: str, *, err: bool = False, shutup: bool = False) -> None:
        """Print an informational message"""
        print(
            "%sINFO: %s%s%s" % (self.BLUE, self.YELLOW, msg, self.RESET),
            file=(_sys.stderr if err else _sys.stdout) if not shutup else _trash,
        )

    def warn(self, msg: str, *, err: bool = False, shutup: bool = False) -> None:
        """Print a warning"""
        print(
            "\N{WARNING SIGN} %sWARNING: %s%s" % (self.YELLOW, msg, self.RESET),
            file=(_sys.stderr if err else _sys.stdout) if not shutup else _trash,
        )

    def error(self, msg: str, errorcode: int = 1) -> NoReturn:
        """Raise an error"""
        raise Exception(msg, errorcode)

    def success(self, msg: str = "Success!", *, err: bool = False) -> None:
        """Print a success message"""
        print(
            "%s%s%s" % (self.GREEN, msg, self.RESET),
            file=(_sys.stderr if err else _sys.stdout),
        )


Colors = Interface
Color, Colour, Colours = Colors, Colors, Colors
color_obj = Color()

TERM_SIZE, COLUMNS, LINES = (
    color_obj.TERM_SIZE,
    color_obj.COLUMNS,
    color_obj.LINES,
)

BLACK: str = color_obj.black
WHITE: str = color_obj.white
RED: str = color_obj.red
BLUE: str = color_obj.blue
YELLOW: str = color_obj.yellow
GREEN: str = color_obj.green
MAGENTA: str = color_obj.magenta
CYAN: str = color_obj.cyan
RESET: str = color_obj.reset
BOLD: str = color_obj.bold

BACKGROUND_BLACK: str = _ansi_prefix + "40m"
BACKGROUND_WHITE: str = _ansi_prefix + "47m"
BACKGROUND_RED: str = _ansi_prefix + "41m"
BACKGROUND_BLUE: str = _ansi_prefix + "44m"
BACKGROUND_YELLOW: str = _ansi_prefix + "43m"
BACKGROUND_GREEN: str = _ansi_prefix + "42m"
BACKGROUND_MAGENTA: str = _ansi_prefix + "45m"
BACKGROUND_CYAN: str = _ansi_prefix + "46m"

_trash = open(_os.devnull, "w")

info, warn, error, success = (
    color_obj.info,
    color_obj.warn,
    color_obj.error,
    color_obj.success,
)
