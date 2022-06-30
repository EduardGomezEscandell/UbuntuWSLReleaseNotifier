#!/usr/bin/python3
import sys
import subprocess
import re
import argparse
import datetime
import os
import json

from typing import List, Tuple, Dict


_CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")


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


def _parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Displays a message if there is an Ubuntu update available, does nothing otherwise.')

    parser.add_argument(
        '-v', '--verbose', dest='verbose', action='store_true', help='enable verbose mode')
    parser.add_argument(
        '-t', '--timeout', dest='timeout', type=float, metavar='SECONDS', default=1.5,
        help='set a timeout for the upgrade querry.')
    parser.add_argument(
        '-f', '--set-frequency', dest='frequency', type=str, choices=_frequecies().keys(),
        help="set the frequency at which you are notified"
    )

    return parser.parse_args()


def _read_config(verbose: bool) -> str:
    _log(verbose, f"Reading file {_CONFIG_FILE}")
    with open(_CONFIG_FILE, "r") as f:
        text = f.read()
        if text:
            return json.loads(text)
        else:
            return None


def _write_config(config: dict, verbose: bool) -> None:
    _log(verbose, f"Updating file {_CONFIG_FILE}")
    with open(_CONFIG_FILE, "w") as f:
        f.write(json.dumps(config, indent=2))


def _set_frequency(frequency: str, verbose: bool = False) -> int:
    if frequency not in _frequecies():
        _log(verbose, f"Frequency '{frequency}' unknown. Use --help to see the options.")
        return 1

    config = {}
    try:
        config = _read_config(verbose)
    except FileNotFoundError:
        _log(verbose, f"File {_CONFIG_FILE} not found, creating it anew.")
    except Exception:
        _log(verbose, f"File {_CONFIG_FILE} invalid, creating it anew.")

    if "last_notif" not in config:
        config["last_notif"] = "1900-01-01T00:00:00+00:00"
    config["notification_frequency"] = frequency

    try:
        _write_config(config, verbose)
        return 0
    except Exception as e:
        return (1, e)


def _check_frequency(verbose: bool) -> Tuple[int, bool]:
    _log(verbose, f"Reading file {_CONFIG_FILE}")

    now = datetime.datetime.now().astimezone()

    try:
        config = _read_config(verbose)
    except Exception as e:
        return (1, e)

    if "notification_frequency" not in config:
        config["notification_frequency"] = "daily"

    if "last_notif" not in config:
        config["last_notif"] = now.isoformat()

    last_notif = datetime.datetime.fromisoformat(config["last_notif"])
    validator = _frequecies()[config["notification_frequency"]]

    must_notify = validator(now, last_notif)

    if must_notify:
        config["last_notif"] = now.isoformat()

    try:
        _write_config(config, verbose)
    except Exception as e:
        return (1, e)

    return (0, must_notify)


def print_or_raise(errcode: int, message_or_exception, verbose: bool) -> int:
    if not errcode and message_or_exception:
        _log(True, message_or_exception)
    elif not errcode:
        _log(verbose, "NO MESSAGE")
    elif errcode and verbose:
        raise message_or_exception
    return errcode


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

    if args.frequency:
        return _set_frequency(args.frequency, args.verbose)

    errcode, must_run = _check_frequency(args.verbose)

    if not must_run:
        return print_or_raise(errcode, must_run, args.verbose)

    errcode, msg = upgrade_message("do-release-upgrade", "-c", verbose=args.verbose, timeout=args.timeout)
    return print_or_raise(errcode, msg, args.verbose)


if __name__ == '__main__':
    sys.exit(main())
