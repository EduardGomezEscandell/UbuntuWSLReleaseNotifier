#!/usr/bin/python3
import sys
import subprocess
import re
from typing import List


def upgrade_message(update_query_command: str, *flags: List[str], verbose=False) -> str:
    full_command = [update_query_command, *flags]
    release_update_response = subprocess.run(full_command, capture_output=True).stdout.decode("utf-8")
    if verbose:
        print("> " + release_update_response.replace("\n", "\n> "))

    result = re.search(r"New release '(.*)' available\.", release_update_response)
    if not result:
        return ""

    release = result.group(1)
    return "\n".join([
        "Release available",
        "=================",
        f"A new release of Ubuntu is available: Ubuntu {release}",
        "To know more, run do-release-upgrade",
        "To disable or change the frequency of these alerts,",
        "read and modify file /etc/update-manager/release-upgrades",
    ])


def _help() -> str:
    print("Displays a message if there is an Ubuntu update")
    print("available, does nothing otherwise. It is intended")
    print("to be called from .bashrc or .profile.")
    print("Usage: notify.py [FLAG]")
    print("Flags: ")
    print("  -v                Enables verbose mode")
    print("  -h or --help      Prints this screen")


def _parse_arguments() -> bool:
    argv = set(sys.argv[1:])

    if "-h" in argv or "--help" in argv:
        _help()
        sys.exit(0)

    verbose = False
    if "-v" or "--verbose" in argv:
        argv.difference_update({"-v", "--verbose"})
        verbose = True

    if argv:
        _help()
        print()
        print(f"Unknown argument{'s' if len(argv) > 1 else ''}: ")
        [print(f"    {a}") for a in argv]
        sys.exit(1)

    return verbose


def main() -> int:
    verbose = _parse_arguments()
    try:
        msg = upgrade_message("do-release-upgrade", "-c", verbose=verbose)
        if msg:
            print(msg)
        elif verbose:
            print("NO MESSAGE")
        return 0
    except Exception as e:
        if verbose:
            raise e
        return 1


if __name__ == '__main__':
    sys.exit(main())
