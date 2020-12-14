"""Utilities for todol"""

import abc as _abc
import datetime as _datetime
import os as _os
import shutil as _shutil
import sys as _sys
from pathlib import Path as _Path
from typing import Any, Callable, Tuple, Union

from . import _interface as interface

today = _datetime.date.today()
tomorrow = today.replace(day=today.day + 1)
users_shell = shell = _Path(
    _os.environ.get("SHELL", (_shutil.which("bash") or "/bin/bash"))
).name


def add_success(success_message: str = "Success!") -> Callable[..., Any]:  # type: ignore
    """A decorator that will add a success message to the end of the function.

    Parameters
    ----------
    success_message : str, optional
        The success message to display (the default is "Success!").

    Returns
    -------
    Callable[..., Any]
        A callable that will return nothing.

    Examples
    --------
    Example:

    >>> @add_success()
    ... def some_func(message):
    ...     print(f"I said {message}!")
    >>> some_func("Hello, world!")
    I said Hello, world!!
    \033[32mSuccess!\033[0m

    Or with arguments:

    >>> @add_success("Done!")
    ... def some_func(message):
    ...     print(f"I said {message}!")
    >>> some_func("Hello, world!")
    I said Hello, world!!
    \033[32mDone!\033[0m


    """

    def parameter_wrapper(func: Callable[..., Any]) -> Callable[..., Any]:  # type: ignore
        def wrapper(*args: Any, **kwargs: Any) -> Any:  # type: ignore
            value = func(*args, **kwargs)  # type: ignore
            interface.success(success_message)
            return value  # type: ignore

        return wrapper  # type: ignore

    return parameter_wrapper  # type: ignore


def fuzzy_match(
    first_string: str, second_string: str, limit: int = 5
) -> Union[bool, int]:
    """A fuzzy match function

    See Also
    --------
    The code this function was based on : http://rosettacode.org/wiki/Levenshtein_distance#Python

    Parameters
    ----------
    first_string, second_string : str
        The two strings to compare against each other.
    limit : int, optional
        The simularity limit in order for
        :param first_string: and :param second_string: to be considered similar (the defualt is 5).

        .. note:: If `limit` is lower than 0, then it implies an infinite limit

    Returns
    -------
    Union[bool, int]
        A boolean value indicating whether `first_string` and `second_string` fuzzy matched.
        If :param limit: is is lower than 0 (i.e. allowing an infinite limit) than this
        function will return an integer value representing the
        `levenshtein distance <https://en.wikipedia.org/wiki/Levenshtein_distance>`
        between `first_string` and `second_string`.

    """

    def result(distance: int) -> Union[bool, int]:
        return distance if limit < 0 else (not distance > limit)

    if first_string == second_string:
        return result(0)

    len_first, length_b = len(first_string), len(second_string)
    if abs(len_first - length_b) > limit >= 0:
        return result(limit + 1)
    if len_first == 0:
        return result(length_b)
    if length_b == 0:
        return result(len_first)
    if length_b > len_first:
        first_string, second_string, len_first, length_b = (
            second_string,
            first_string,
            length_b,
            len_first,
        )

    cost = list(range(length_b + 1))
    for i in range(1, len_first + 1):
        cost[0] = i
        l_s = i - 1
        minimum = l_s
        for j in range(1, length_b + 1):
            l_s, act = cost[j], l_s + int(first_string[i - 1] != second_string[j - 1])
            cost[j] = min(l_s + 1, cost[j - 1] + 1, act)
            if l_s < minimum:
                minimum = l_s
        if minimum > limit >= 0:
            return result(limit + 1)
    return result(limit + 1) if cost[length_b] > limit >= 0 else result(cost[length_b])


def parse_isoformat_date(dtstr: str) -> Tuple[int, int, int]:
    """A backport of _parse_isoformat_date. Returns a tuple instead of a list"""
    if not isinstance(dtstr, str):
        raise TypeError(f"argument must be str, not {type(dtstr).__name__}")

    try:
        assert len(dtstr) == 10
        year = int(dtstr[0:4])
        if dtstr[4] != "-":
            raise ValueError("Invalid date separator: %s" % dtstr[4])

        month = int(dtstr[5:7])

        if dtstr[7] != "-":
            raise ValueError("Invalid date separator")

        day = int(dtstr[8:10])

        return year, month, day
    except Exception as exception:
        raise ValueError(f"Invalid isoformat string: {dtstr!r}") from exception


def iso_str_to_datetime(string: str) -> _datetime.date:
    """Convert a string into a datetime.date object.

    For serialization datetime.date objects from a
    string in ISO 8601 format (YYYY-MM-DD) for argparse/click.
    """
    return _datetime.date(*parse_isoformat_date(string))


def sim_str(string: str) -> str:
    """Makes a string consistant"""
    return string.lower().strip()


def yes_or_no(prompt: str = "", default: bool = True, err: bool = True) -> bool:
    processed_default = (
        interface.BOLD
        + interface.BLUE
        + ("[Y/n]" if default else "[y/N]")
        + interface.RESET
    )
    processed_prompt = f"{interface.YELLOW}{prompt}{interface.RESET}"
    while True:
        try:
            answer: Union[str, bool] = (
                input(f"{processed_prompt}{processed_default}: ").lower().strip()
            )
        except (KeyboardInterrupt, EOFError):
            print(f"\n{interface.YELLOW}Cancelled!{interface.RESET}")
            answer = False
            break
        if answer in ("y", "yes"):
            answer = True
        elif answer in ("n", "no"):
            answer = False
        elif answer == "":
            answer = default
        else:
            interface.error("invalid input", err=err)
            continue
        break
    return answer


class Deserializable(metaclass=_abc.ABCMeta):  # pylint: disable=too-few-public-methods
    """A base class for deserializable objects"""

    @_abc.abstractmethod
    def __deserialize__(self) -> Any:  # type: ignore
        pass


def deserialize(obj: Deserializable) -> Any:
    """Deserialize an object"""
    if not (hasattr(obj, "__deserialize__") or issubclass(obj, Deserializable)):  # type: ignore
        raise TypeError("Expected a Deserializable object not %s" % type(obj).__name__)
    return obj.__deserialize__()  # type: ignore


def initialize_shell(version: str) -> None:
    to_inject = (
        f"# >>> Section managed/injected by Todol {version}>>>\n"
        + f"{_sys.executable} -m {_Path(__file__).parent} list\n"
        + "# <<<<<<\n"
    )

    # Calculate the rc file
    rc_file_path = _Path(f"~/.{users_shell}rc").expanduser()
    if not (rc_file_path.exists() and rc_file_path.is_file()):
        rc_file_path.touch()

    # Get rc file contents
    to_append = rc_file_path.read_text()

    print(
        "Would you also like to "
        f"{interface.BOLD}see your todos{interface.RESET} "
        "at the start of every shell session?"
    )

    # Shell injection logic
    if not to_append.startswith(to_inject) and yes_or_no():

        # Append the following to the rc file:
        # # >>> Section managed/injected by Todol [PROGRAM VERSION] >>>
        # [PYTHON EXECUTABLE] [THIS FILE] list
        # # <<<<<<
        interface.info(f"Injecting to {rc_file_path}...")

        assert not to_append.startswith(to_inject)

        # Inject!
        rc_file_path.write_text(to_inject + to_append)

        interface.success()

        # Why at the top of the file?
        # To make sure that the command is properly executed
        # so things like Powerlevel10k's "instant prompt"
        # won't get bothered.
        # We also use sys.executable and __file__
        # to throw all that $PATH mess out the window
    else:
        interface.success("Cancelled!")
