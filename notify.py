#!/usr/bin/python3
import sys
import subprocess
import re
import argparse

from typing import List, Tuple


def upgrade_message(update_query_cmd: str, *flags: List[str], verbose: bool = False, timeout: float = 5) -> Tuple[int, str]:
    full_command = [update_query_cmd, *flags]

    try:
        release_update_response = subprocess.check_output(
            full_command, text=True, encoding="utf-8", stderr=subprocess.STDOUT, timeout=timeout)
    except subprocess.SubprocessError as e:
        if verbose:
            raise e
        return (1, e)

    if verbose:
        print("> " + release_update_response.replace("\n", "\n> "))

    result = re.search(r"New release '(.*)' available\.", release_update_response)
    if not result:
        return (0, "")

    release = result.group(1)
    return (0, "Release available\n"
               "=================\n"
               f"A new release of Ubuntu is available: Ubuntu {release}\n"
               "To know more, run do-release-upgrade\n"
               "To disable or change the frequency of these alerts,\n"
               "read and modify file /etc/update-manager/release-upgrades"
            )


def _parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Displays a message if there is an Ubuntu update available, does nothing otherwise.')

    parser.add_argument(
        '-v', '--verbose', dest='verbose', action='store_true', help='enable verbose mode')
    parser.add_argument(
        '-t', '--timeout', dest='timeout', type=float, metavar='SECONDS', default=1.5,
        help='set a timeout for the upgrade querry.')

    return parser.parse_args()


def main() -> int:
    config = _parse_arguments()

    errcode, msg = upgrade_message("do-release-upgrade", "-c", verbose=config.verbose, timeout=config.timeout)

    if not errcode and msg:
        print(msg)
    elif not errcode and config.verbose:
        print("NO MESSAGE")

    return errcode


if __name__ == '__main__':
    sys.exit(main())
