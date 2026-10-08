"""Start the packaged app, check that it stays up without multiplying, then close it.

Used by CI. On Windows the window is asked to close the way a user would close it;
elsewhere the app receives SIGTERM. Either way every process has to be gone afterwards.
"""

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


def running_processes() -> int:
    if WINDOWS:
        listing = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq gfl2logger.exe", "/FO", "CSV", "/NH"],
            capture_output=True,
            text=True,
        ).stdout
        return sum(
            line.lower().startswith('"gfl2logger.exe"') for line in listing.splitlines()
        )
    listing = subprocess.run(
        ["pgrep", "-f", "gfl2logger.app/Contents/MacOS/gfl2logger"],
        capture_output=True,
        text=True,
    ).stdout
    return len(listing.split())


def force_stop(process: subprocess.Popen) -> None:
    if WINDOWS:
        subprocess.run(
            ["taskkill", "/F", "/T", "/IM", "gfl2logger.exe"], capture_output=True
        )
    else:
        subprocess.run(
            ["pkill", "-9", "-f", "gfl2logger.app/Contents/MacOS/gfl2logger"],
            capture_output=True,
        )
    process.wait(timeout=30)


def main(executable: str) -> int:
    # Windows builds write exports and settings to the working directory.
    workdir = tempfile.mkdtemp(prefix="gfl2logger-smoke-")
    process = subprocess.Popen([executable], cwd=workdir)

    time.sleep(STARTUP_SECONDS)
    started = running_processes()
    print(f"processes after {STARTUP_SECONDS}s: {started}")
    if process.poll() is not None:
        print(f"FAIL: exited during start-up with code {process.returncode}")
        return 1
    if not 2 <= started <= MAX_PROCESSES:
        print(f"FAIL: expected 2..{MAX_PROCESSES} processes")
        force_stop(process)
        return 1

    if WINDOWS:
        # Without /F this posts WM_CLOSE to the window, like clicking its close button.
        subprocess.run(["taskkill", "/IM", "gfl2logger.exe"], capture_output=True)
    else:
        process.terminate()

    deadline = time.monotonic() + SHUTDOWN_SECONDS
    while time.monotonic() < deadline and running_processes():
        time.sleep(1)
    remaining = running_processes()
    if remaining:
        print(f"FAIL: {remaining} processes still running after closing")
        force_stop(process)
        return 1

    print("OK: started, stayed bounded, and exited completely when closed")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
