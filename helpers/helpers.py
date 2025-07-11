"""Helper functions for the ride scheduling script.

This module contains various helper functions that are used by the ride
scheduling script. These functions provide utility functionality such as
converting between different data types, printing text in-place, and
updating nested dictionaries.
"""
import shutil


def strip_useless_info(rides: list[dict]) -> list[dict]:
    """Strip unnecessary information from a list of ride dictionaries.

    This function takes a list of raw ride dictionaries from the server and
    removes information that is not used in this script in order to save on
    memory usage on the system.

    Args:
        rides: The list of raw ride dictionaries to strip.

    Returns:
        A list of stripped ride dictionaries.
    """
    return [{
        "time": ride["occasions"][0]["time"],
        'location':ride["occasions"][0]["locationName"],
        'cost':ride["occasions"][0]["cost"],
        'date':ride["occasions"][0]["date"],
        'name':ride["occasions"][0]["name"]
    } for ride in rides]


def inplace_print(output: str) -> None:
    """Print a string in-place.

    This function prints a string to the console and overwrites the current
    line of text without adding new lines to the console.

    Args:
        s: The string to print.
    """
    print(output, end="\r", flush=True)


def hide_print(terminal_width: int = None) -> None:
    """Clear the current line on the console.

    This function prints whitespace to the console, overwriting
    the current line of text, and then moves the cursor to the
    beginning of the line. This has the effect of "hiding" the
    current line of text without adding new lines to the console.

    Args:
        terminal_width: The width of the terminal in characters.
            If not provided, the width of the terminal will be
            determined using the shutil module.
    """
    if terminal_width is None:
        (terminal_width, _) = list(shutil.get_terminal_size((80, 20)))

    print(" " * terminal_width, end="\r", flush=True)


