#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# type: ignore
"""
Initial author: Bryan Hu.

@ThatXliner.

Version: v0.1.0

A file of parsers for argparse

"""
import argparse as _argparse
import os as _os

__all__ = ["color_options"]
color_options: _argparse.ArgumentParser = _argparse.ArgumentParser(add_help=False)


class BooleanOptionalAction(_argparse.Action):
    """A backport of argparse.BooleanOptionalAction"""

    # pylint: disable=C,R,W
    def __init__(
        self,
        option_strings,
        dest,
        default=None,
        type=None,
        choices=None,
        required=False,
        help=None,
        metavar=None,
    ):

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
            default=default,
            type=type,
            choices=choices,
            required=required,
            help=help,
            metavar=metavar,
        )

    def __call__(self, parser, namespace, values, option_string=None):
        if option_string in self.option_strings:
            setattr(namespace, self.dest, not option_string.startswith("--no-"))

    def format_usage(self):
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
