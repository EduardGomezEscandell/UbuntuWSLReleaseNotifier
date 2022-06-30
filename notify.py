#!/usr/bin/python3
import sys
import subprocess
import re
import argparse
import datetime
import os

from typing import List, Tuple, Dict


_TIMESTAMP_FILE = os.path.join(os.path.dirname(__file__), "last_notification_timestamp")


def _log(enable: bool, *message) -> None:
    if enable:
        print(*message)


def _frequecies() -> Dict[str, int]:
    freqs = {
        "always": lambda *_: True,
        "never": lambda *_: False,
        "hourly": lambda now, last: (now - last).seconds >= 3600,
        "daily": lambda now, last: (now - last).days >= 1,
        "weekly": lambda now, last: (now - last).days >= 7,
        "monthly": lambda now, last: (now - last).days >= 30,
        "yearly": lambda now, last: (now - last).days >= 365,
    }
    return freqs


def _read_timestamp(verbose: bool) -> datetime.datetime:
    _log(verbose, f"Reading file {_TIMESTAMP_FILE}")
    try:
        with open(_TIMESTAMP_FILE, "r") as f:
            return datetime.datetime.fromisoformat(f.read())
    except Exception as e:
        _log(verbose, f"Failed to read timestamp: {e.what}")
        return datetime.datetime(1900, 1, 1).astimezone()


def _write_timestamp(timestamp: datetime.datetime, verbose: bool) -> None:
    _log(verbose, f"Updating file {_TIMESTAMP_FILE}")
    try:
        with open(_TIMESTAMP_FILE, "w") as f:
            f.write(timestamp.isoformat())
    except Exception as e:
        _log(verbose, f"Failed to write timestamp: {e.what}")


def _print_or_raise(errcode: int, message_or_exception, verbose: bool) -> int:
    if not errcode and message_or_exception:
        _log(True, message_or_exception)
    elif not errcode:
        _log(verbose, "NO MESSAGE")
    elif errcode and verbose:
        raise message_or_exception
    return errcode


def _parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Displays a message if there is an Ubuntu update available, does nothing otherwise.')

    parser.add_argument(
        '-v', '--verbose', dest='verbose', action='store_true', help='enable verbose mode')
    parser.add_argument(
        '-t', '--timeout', dest='timeout', type=float, metavar='SECONDS', default=1.5,
        help='set a timeout for the upgrade querry.')
    parser.add_argument(
        '-f', '--frequency', dest='frequency', type=str, choices=_frequecies().keys(),
        default="daily", help="set the frequency at which you are notified"
    )

    return parser.parse_args()


def _check_frequency(frequency: str, verbose: bool) -> bool:
    last_notif = _read_timestamp(verbose)
    validator = _frequecies()[frequency]
    now = datetime.datetime.now().astimezone()
    _write_timestamp(now, verbose)
    return validator(now, last_notif)


def upgrade_message(update_query_cmd: str, *flags: List[str], verbose: bool = False, timeout: float = 5) -> Tuple[int, str]:
    full_command = [update_query_cmd, *flags]

    try:
        release_update_response = subprocess.check_output(
            full_command, text=True, encoding="utf-8", stderr=subprocess.STDOUT, timeout=timeout)
    except subprocess.SubprocessError as e:
        return (1, e)

    _log(verbose, "> " + release_update_response.replace("\n", "\n> "))

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


def main() -> int:
    args = _parse_arguments()

    if not _check_frequency(args.frequency, args.verbose):
        return 0

    errcode, msg = upgrade_message("do-release-upgrade", "-c", verbose=args.verbose, timeout=args.timeout)
    return _print_or_raise(errcode, msg, args.verbose)


if __name__ == '__main__':
    sys.exit(main())
