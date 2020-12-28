#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Initial author: Bryan Hu.

@ThatXliner.

Version: v0.1.0

A file of parsers for argparse

"""
import argparse as _argparse
import os as _os
from typing import Any, Callable, Optional, Sequence, Tuple

from . import _utils

__all__ = ["color_options", "due_date_options"]
color_options: _argparse.ArgumentParser = _argparse.ArgumentParser(add_help=False)


class BooleanOptionalAction(_argparse.Action):
    """A backport of argparse.BooleanOptionalAction"""

    # pylint: disable=C,R,W
    def __init__(
        self,
        option_strings: Tuple[str, ...],
        dest: str,
        default: Optional[Any] = None,
        type: Optional[Callable[[str], Any]] = None,
        choices: Optional[Sequence[str]] = None,
        required: bool = False,
        help: Optional[str] = None,
        metavar: Optional[str] = None,
    ) -> None:

        _option_strings = []
        for option_string in option_strings:
            _option_strings.append(option_string)

            if option_string.startswith("--"):
                option_string = "--no-" + option_string[2:]
                _option_strings.append(option_string)

        # if help is not None and default is not None:
        #     help += f" (default: {default})"

        super().__init__(
            option_strings=_option_strings,
            dest=dest,
            nargs=0,
            default=default,  # type: ignore
            type=type,  # type: ignore
            choices=choices,
            required=required,
            help=help,
            metavar=metavar,
        )

    def __call__(self, parser, namespace: _argparse.Namespace, values, option_string: Optional[str] = None) -> None:  # type: ignore
        if option_string in self.option_strings:
            assert isinstance(option_string, str)
            setattr(namespace, self.dest, not option_string.startswith("--no-"))

    def format_usage(self) -> str:
        return " | ".join(self.option_strings)


opts = color_options.add_mutually_exclusive_group()

opts.add_argument(
    "--no-color",
    action="store_true",
    help="Don't print color",
    dest="no_color",
    default=bool(int(_os.environ.get("TODOL_FORCE_COLOR", 0))),
)
opts.add_argument(
    "--force-color",
    action="store_true",
    help="Force color output even if not printing to a terminal",
    dest="force_color",
    default=bool(int(_os.environ.get("TODOL_FORCE_COLOR", 0))),
)
due_date_options: _argparse.ArgumentParser = _argparse.ArgumentParser(add_help=False)
due_dates = due_date_options.add_mutually_exclusive_group()
due_dates.add_argument(  # TODO: Add time capability
    "--due",
    "--due-date",
    "-d",
    default=str(_utils.tomorrow),
    type=str,
    help="The due date in ISO 8601 format, YYYY-MM-DD (padded with zeros, if required)",
    dest="due_date",
)
due_dates.add_argument(
    "--long-term",
    "--long",
    "-l",
    action="store_true",
    help="Make the todo a long term goal",
    dest="long_term",
)
