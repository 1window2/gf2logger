"""Start the packaged app, check that it stays up without multiplying, then close it.

Used by CI. On Windows the window process is asked to close the way a user would close
it; elsewhere the app receives SIGTERM. Either way every process has to be gone
afterwards.
"""

import json
import os
import subprocess
import sys
import tempfile
import time

STARTUP_SECONDS = 25
SHUTDOWN_SECONDS = 60
# The proxy, the window process and their launcher/helper processes. A frozen build that
# re-launches itself during multiprocessing start-up blows far past this.
MAX_PROCESSES = 8
WINDOWS = sys.platform == "win32"
MACOS_PATTERN = "gfl2logger.app/Contents/MacOS/gfl2logger"


def processes() -> list[dict]:
    """Return pid, parent pid and command line of every running app process."""
    if WINDOWS:
        listing = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "Get-CimInstance Win32_Process -Filter \"name='gfl2logger.exe'\" | "
                "Select-Object ProcessId,ParentProcessId,CommandLine | ConvertTo-Json",
            ],
            capture_output=True,
            text=True,
        ).stdout.strip()
        if not listing:
            return []
        found = json.loads(listing)
        found = [found] if isinstance(found, dict) else found
        return [
            {
                "pid": item["ProcessId"],
                "parent": item["ParentProcessId"],
                "command": item["CommandLine"] or "",
            }
            for item in found
        ]

    listing = subprocess.run(
        ["ps", "-axo", "pid=,ppid=,command="], capture_output=True, text=True
    ).stdout
    found = []
    for line in listing.splitlines():
        pid, parent, command = line.split(None, 2)
        if MACOS_PATTERN in command:
            found.append({"pid": int(pid), "parent": int(parent), "command": command})
    return found


def describe(found: list[dict]) -> None:
    for item in found:
        print(f"  pid={item['pid']} parent={item['parent']} {item['command']}")


def force_stop(process: subprocess.Popen) -> None:
    if WINDOWS:
        subprocess.run(
            ["taskkill", "/F", "/T", "/IM", "gfl2logger.exe"], capture_output=True
        )
    else:
        subprocess.run(["pkill", "-9", "-f", MACOS_PATTERN], capture_output=True)
    process.wait(timeout=30)


def close(process: subprocess.Popen, found: list[dict]) -> None:
    if not WINDOWS:
        process.terminate()
        return
    # The window lives in the multiprocessing child. Without /F, taskkill posts WM_CLOSE
    # to that process, which is what clicking the window's close button does.
    windows = [item for item in found if "--multiprocessing-fork" in item["command"]]
    for item in windows:
        result = subprocess.run(
            ["taskkill", "/PID", str(item["pid"])], capture_output=True, text=True
        )
        print(f"close request to pid={item['pid']}: {result.stdout.strip()}")
    if not windows:
        print("no window process found to close")


def main(executable: str) -> int:
    executable = os.path.abspath(executable)
    # Windows builds write exports and settings to the working directory.
    workdir = tempfile.mkdtemp(prefix="gfl2logger-smoke-")
    process = subprocess.Popen([executable], cwd=workdir)

    time.sleep(STARTUP_SECONDS)
    started = processes()
    print(f"processes after {STARTUP_SECONDS}s: {len(started)}")
    describe(started)
    if process.poll() is not None:
        print(f"FAIL: exited during start-up with code {process.returncode}")
        return 1
    if not 2 <= len(started) <= MAX_PROCESSES:
        print(f"FAIL: expected 2..{MAX_PROCESSES} processes")
        force_stop(process)
        return 1

    close(process, started)
    deadline = time.monotonic() + SHUTDOWN_SECONDS
    while time.monotonic() < deadline and processes():
        time.sleep(1)
    remaining = processes()
    if remaining:
        print(f"FAIL: {len(remaining)} processes still running after closing")
        describe(remaining)
        force_stop(process)
        return 1

    print("OK: started, stayed bounded, and exited completely when closed")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
