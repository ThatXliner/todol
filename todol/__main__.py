#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Initial author: Bryan Hu.

@ThatXliner.

Version: v0.1.0

The main cli entry point

"""
import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List

from . import __version__
from . import _interface as intf
from . import _utils, todo_objects
from ._opts import color_options, due_date_options

parser = argparse.ArgumentParser(
    description="A todo list CLI tool",
    prog="todol",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    parents=[color_options],
)
parser.add_argument(
    "--version", action="version", version="%(prog)s {}".format(__version__)
)

subparsers = parser.add_subparsers(dest="command")

list_parser = subparsers.add_parser(
    "list", help="List todos", aliases=("l"), parents=[color_options]
)
list_display_choices = list_parser.add_mutually_exclusive_group()
list_display_choices.add_argument(
    "--finished",
    "--fin",
    help="Show finished todos",
    action="store_true",
    dest="show_finished",
)
list_display_choices.add_argument(
    "--all",
    help="Show all todos, whether finished or not",
    action="store_true",
    dest="show_all",
)

init_parser = subparsers.add_parser(
    "init", help="Initialize todol", parents=[color_options]
)
init_parser.add_argument(
    "--no-shell",
    action="store_true",
    help="Don't inject a todo-listing command to your shell's rc file",
    dest="no_shell",
)

add_parser = subparsers.add_parser(
    "add", help="Add a todo", aliases=("a"), parents=[color_options, due_date_options]
)
add_parser.add_argument("todo", help="The todo to add.", type=_utils.sim_str)


remove_parser = subparsers.add_parser(
    "remove",
    help="Remove todo(s) without finishing them",
    aliases=("r", "remove"),
    parents=[color_options, due_date_options],
)
remove_parser.add_argument(
    "todo",
    help="The todo to remove. Will be fuzzy matched or matched by ID/date/etc",
)

finish_parser = subparsers.add_parser(
    "finish",
    help="Finish todo(s)",
    aliases=("f", "do"),
    parents=[color_options, due_date_options],
)
finish_parser.add_argument(
    "todo",
    help="The todo to finish. Will be fuzzy matched or matched by ID/date/etc",
)


completion_parser = subparsers.add_parser(
    "complete",
    help="Generate shell completion. The pycomplete library must be installed, though.",
    aliases=("c", "completion"),
)
completion_parser.add_argument(
    "shell",
    nargs="?",
    choices=("zsh", "bash", "fish", "powershell"),
    default=_utils.users_shell,
)
parser.set_defaults(no_shell=False)  # See line 244
args = parser.parse_args()


def main() -> None:  # TODO: REFACTOR this to an object
    """The main entry point function."""

    todol_dir = Path(os.environ.get("TODOL_CONFIG_DIR", "~/.config/todol")).expanduser()
    todo_index = todol_dir.joinpath("todos.json")
    interface = intf.Color(no_color=args.no_color, force_color=args.force_color)  # type: ignore

    def _get_todo_data() -> Dict[str, List[Dict[str, str]]]:
        try:
            todos: Dict[str, List[Dict[str, str]]] = json.loads(todo_index.read_text())
        except OSError:  # It doesn't exist
            interface.softerror("Todol is not initialized!")
            command_init()
            todos = json.loads(todo_index.read_text())
        assert isinstance(todos, dict)
        return todos

    def command_list() -> int:
        todos = _get_todo_data()

        def show_todo() -> None:
            for item in todo_objects.TodoContainer(todos["todos"]):
                print(
                    f" - {interface.BLUE}{item.name!r}{interface.RESET}, "
                    f"{interface.RED}due at {interface.YELLOW}{item.due_date}{interface.RESET}"
                )

        def show_finished() -> None:
            for item in todo_objects.TodoContainer(todos["finished"]):
                print(f" - {interface.GREEN}{item.name!r}{interface.RESET}")

        print("-" * int(interface.COLUMNS / 3))
        if not (args.show_all or args.show_finished):  # type: ignore
            if not todos["todos"]:
                print("\N{PARTY POPPER} No todos!")
            show_todo()
        elif args.show_finished:  # type: ignore
            show_finished()
        else:
            show_todo()
            show_finished()
        print("-" * int(interface.COLUMNS / 3))
        return 0

    def command_add() -> int:
        todos = _get_todo_data()
        assert isinstance(args.todo, str)  # type: ignore

        interface.info(f"Adding todo {args.todo!r} to the list of todos...")
        todo_obj = todo_objects.TodoContainer(todos["todos"])
        todo_obj.add_todo({"todo": args.todo, "due_date": args.due_date})  # type: ignore
        todos["todos"] = _utils.deserialize(todo_obj)  # type: ignore

        # Actually add it to the the list of todos
        todo_index.write_text(json.dumps(todos))
        interface.success("Done!")
        return 0

    def command_remove() -> int:
        todos = _get_todo_data()
        assert isinstance(args.todo, str)  # type: ignore

        interface.info(f"Removing todo {args.todo!r}...")
        todo_obj = todo_objects.TodoContainer(todos["todos"])

        try:
            todo_obj.pop_thing({"todo": args.todo, "due_date": args.due_date})  # type: ignore
        except IndexError:
            interface.error("Could not find todo!", 1)

        else:
            todos["todos"] = _utils.deserialize(todo_obj)  # type: ignore
            # Actually add it to the index
            todo_index.write_text(json.dumps(todos))
            interface.success("Done!")
            return 0

    def command_finish() -> int:
        todos = _get_todo_data()
        assert isinstance(args.todo, str)  # type: ignore

        interface.info(f"Finishing todo {args.todo!r}...")

        todo_obj = todo_objects.TodoContainer(todos["todos"])
        finished_obj = todo_objects.TodoContainer(todos["finished"])
        try:
            finished_obj.add_todo(
                todo_obj.pop_thing({"todo": args.todo, "due_date": args.due_date})  # type: ignore
            )
        except IndexError:
            interface.error("Could not find todo!", 1)
        else:
            todos["finished"] = _utils.deserialize(finished_obj)  # type: ignore
            todos["todos"] = _utils.deserialize(todo_obj)  # type: ignore

            # Actually add it to the index
            todo_index.write_text(json.dumps(todos))
            interface.success("Done!")
            return 0

    def command_init() -> int:
        """Initialize todol for the current user."""

        if not (todol_dir.is_dir() and todol_dir.exists()):
            interface.info(f"Creating todol directory at {todol_dir}...")
            todol_dir.mkdir(parents=True)  # Also make ~/.config if it doesn't exist
            interface.success()

        if not (todo_index.is_file() and todo_index.exists()):
            interface.info("Creating todol index...")
            todo_index.touch()  # Create todol.json
            interface.success()

        if not todo_index.read_text():  # Empty
            todo_index.write_text(R'{"todos":[], "finished":[]}')

        if not args.no_shell:  # type: ignore  # default to False
            _utils.initialize_shell(__version__)
        interface.success("\N{SPARKLES} Initialized todol!")
        return 0

    def command_complete() -> int:
        try:
            import pycomplete  # type:ignore # pylint: disable=C0415
        except ModuleNotFoundError:
            interface.error(
                "Pycomplete not installed! "
                "Please install the extra via `pip install todol[complete]`",
                1,
            )
        else:
            completer = pycomplete.Completer(parser)  # type: ignore
            print(completer.render(args.shell))  # type: ignore
            return 0

    subcommands_map = {
        "list": command_list,
        "l": command_list,
        "add": command_add,
        "a": command_add,
        "remove": command_remove,
        "r": command_remove,
        "finish": command_finish,
        "f": command_finish,
        "do": command_finish,
        "init": command_init,
        "complete": command_complete,
        "c": command_complete,
    }
    try:
        sys.exit(subcommands_map.get(args.command, parser.print_help)() or 0)  # type: ignore
    except Exception as exception:  # pylint: disable=broad-except
        value = exception.args[0]  # type: ignore
        if len(exception.args) == 1:  # type: ignore
            print(f"\N{COLLISION SYMBOL} {interface.RED}{value}{interface.RESET}")  # type: ignore
            sys.exit(1)
        assert len(exception.args) == 2  # type: ignore
        returncode = exception.args[1]  # type: ignore
        assert isinstance(value, str)  # type: ignore
        assert isinstance(returncode, int)  # type: ignore
        print(f"\N{COLLISION SYMBOL} {interface.RED}{value}{interface.RESET}")
        sys.exit(returncode)


if __name__ == "__main__":
    main()
