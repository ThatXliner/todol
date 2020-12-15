#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Initial author: Bryan Hu.

@ThatXliner.

A file containing ansi escape codes for color!

See https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797#color-codes

"""

import os
import platform
import shutil as _shutil
import sys

TERM_SIZE = _shutil.get_terminal_size()
COLUMNS: int = TERM_SIZE.columns
LINES: int = TERM_SIZE.lines
_ansi_prefix: str = "\033["
if sys.stdout.isatty():  # Test if printing to a terminal (or a terminal-like device)
    if platform.system() == "Windows":  # Special Windows support
        try:
            import colorama  # type: ignore

            colorama.init()  # type: ignore
        except ImportError:
            pass

    ###
    # Foreground colors
    ###

    # Monotone
    BLACK: str = _ansi_prefix + "30m"
    WHITE: str = _ansi_prefix + "37m"

    # Primary
    RED: str = _ansi_prefix + "31m"
    BLUE: str = _ansi_prefix + "34m"
    YELLOW: str = _ansi_prefix + "33m"

    # Secondary
    GREEN: str = _ansi_prefix + "32m"
    MAGENTA: str = _ansi_prefix + "35m"
    CYAN: str = _ansi_prefix + "36m"

    # Meta
    RESET: str = _ansi_prefix + "0m"
    BOLD: str = _ansi_prefix + "1m"
    ###
    # Background colors
    ###

    # Monotone
    BACKGROUND_BLACK: str = _ansi_prefix + "40m"
    BACKGROUND_WHITE: str = _ansi_prefix + "47m"

    # Primary
    BACKGROUND_RED: str = _ansi_prefix + "41m"
    BACKGROUND_BLUE: str = _ansi_prefix + "44m"
    BACKGROUND_YELLOW: str = _ansi_prefix + "43m"

    # Secondary
    BACKGROUND_GREEN: str = _ansi_prefix + "42m"
    BACKGROUND_MAGENTA: str = _ansi_prefix + "45m"
    BACKGROUND_CYAN: str = _ansi_prefix + "46m"
else:  # Strip ANSI if not printing to a terminal
    BLACK = (
        WHITE
    ) = (
        RED
    ) = (
        BLUE
    ) = (
        YELLOW
    ) = (
        GREEN
    ) = (
        MAGENTA
    ) = (
        CYAN
    ) = (
        RESET
    ) = (
        BOLD
    ) = (
        BACKGROUND_BLACK
    ) = (
        BACKGROUND_BLUE
    ) = (
        BACKGROUND_YELLOW
    ) = BACKGROUND_GREEN = BACKGROUND_MAGENTA = BACKGROUND_CYAN = ""  # Nothing

_trash = open(os.devnull, "w")


def info(msg: str, *, err: bool = False, shutup: bool = False) -> None:
    """Print an informational message"""
    print(
        "%sINFO: %s%s%s" % (BLUE, YELLOW, msg, RESET),
        file=(sys.stderr if err else sys.stdout) if not shutup else _trash,
    )


def warn(msg: str, *, err: bool = False, shutup: bool = False) -> None:
    """Print a warning"""
    print(
        "\N{WARNING SIGN} %sWARNING: %s%s" % (YELLOW, msg, RESET),
        file=(sys.stderr if err else sys.stdout) if not shutup else _trash,
    )


def error(msg: str, *, err: bool = False, shutup: bool = False) -> None:
    """Print an error message"""
    # TODO: Change error system to make use of exceptions
    print(
        "\N{COLLISION SYMBOL} %sERROR: %s%s" % (RED, msg, RESET),
        file=(sys.stderr if err else sys.stdout) if not shutup else _trash,
    )


def success(msg: str = "Success!", *, err: bool = False) -> None:
    """Print a success message"""
    print("%s%s%s" % (GREEN, msg, RESET), file=(sys.stderr if err else sys.stdout))
