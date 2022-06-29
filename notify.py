#!/usr/bin/python3
import sys
import subprocess
import re

def upgrade_message(upgrade_command: str, *args: list, verbose = False) -> str:
    full_command = [upgrade_command, *args]
    release_update_response = subprocess.run(full_command, capture_output=True).stdout.decode("utf-8")
    if verbose:
        print("> " + release_update_response.replace("\n", "\n> "))
    
    result = re.search(r"New release '(.*)' available\.", release_update_response)
    if not result:
        return None

    release = result.group(1)
    return "\n".join([
        "Release available",
        "=================",
        f"A new release of Ubuntu is available: Ubuntu {release}",
        "To know more, run do-release-upgrade",
        "To disable or change the frequency of these alerts,",
        "read and modify file /etc/update-manager/release-upgrades",
    ])

def main():
    verbose = "-v" in sys.argv
        
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