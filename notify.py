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


def _cooldowns() -> Dict[str, int]:
    return {
        "none": lambda *_: True,
        "hour": lambda now, last: (now - last.get()).total_seconds() >= 3600,
        "day": lambda now, last: (now - last.get()).days >= 1,
        "week": lambda now, last: (now - last.get()).days >= 7,
        "month": lambda now, last: (now - last.get()).days >= 30,
        "year": lambda now, last: (now - last.get()).days >= 365,
        "inf": lambda *_: False,
    }

class _LazyDatetime:
    def __init__(self, verbose) -> None:
        self.verbose = verbose
        self.date = None
    
    def get(self):
        if self.date is not None:
            return self.date
        else:
            self.date = self.__read()
            return self.date

    def _read(self):
        _log(self.verbose, f"Reading file {_TIMESTAMP_FILE}")
        try:
            with open(_TIMESTAMP_FILE, "r") as f:
                return datetime.datetime.fromisoformat(f.read())
        except Exception:
            _log(self.verbose, "Failed to read timestamp")
            return datetime.datetime(1900, 1, 1).astimezone()


def _write_timestamp(timestamp: datetime.datetime, verbose: bool = False) -> None:
    _log(verbose, f"Updating file {_TIMESTAMP_FILE}")
    try:
        with open(_TIMESTAMP_FILE, "w") as f:
            f.write(timestamp.isoformat())
    except Exception:
        _log(verbose, f"Failed to write timestamp")


def _print_or_raise(errcode: int, message_or_exception, verbose: bool = False) -> int:
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
        '-c', '--cooldown', dest='cooldown', type=str, choices=_cooldowns().keys(),
        default="day", help="set a cooldown for this alert"
    )

    return parser.parse_args()


def _check_cooldown(cooldown: str, verbose: bool = False) -> bool:
    last_notif = _LazyDatetime(verbose)
    validator = _cooldowns()[cooldown]
    now = datetime.datetime.now().astimezone()
    if validator(now, last_notif):
        _write_timestamp(now, verbose)
        return True
    return False


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
               "To change the types of updates you are notified about,\n"
               "read and modify file /etc/update-manager/release-upgrades"
            )


def main() -> int:
    args = _parse_arguments()

    if not _check_cooldown(args.cooldown, args.verbose):
        return 0

    errcode, msg = upgrade_message("do-release-upgrade", "-c", verbose=args.verbose, timeout=args.timeout)
    return _print_or_raise(errcode, msg, args.verbose)


if __name__ == '__main__':
    sys.exit(main())
