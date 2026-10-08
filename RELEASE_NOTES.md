# gfl2logger v0.3.0

This release brings the Windows and macOS versions together. Both are now built
from the same code, share one version number, and have the same features,
options, and window. Windows continues from v0.2.5; the macOS line, previously
published as v0.1.x, joins the same numbering.

## Downloads

| Platform | Game client | Download |
| --- | --- | --- |
| **Windows** (x64) | PC client | [`gfl2logger-v0.3.0-windows-x64.exe`](../../releases/download/v0.3.0/gfl2logger-v0.3.0-windows-x64.exe) |
| **macOS** (Apple silicon) | iPhone/iPad version from the Mac App Store | [`gfl2logger-v0.3.0-macos-arm64.dmg`](../../releases/download/v0.3.0/gfl2logger-v0.3.0-macos-arm64.dmg) · [`gfl2logger-v0.3.0-macos-arm64.zip`](../../releases/download/v0.3.0/gfl2logger-v0.3.0-macos-arm64.zip) |

## Changes

### Windows, since v0.2.5

- Added Platoon Profile (`21905`), Activity (`21935`), and Updates (`21960`)
  exports alongside Members, and grouped the options into **Platoon** and
  **Others**.
- Kept message bytes that arrive split across TCP chunks and finished parsing
  data already received when a connection closes, so responses are no longer
  dropped or misread at chunk boundaries.
- Released forwarded TCP messages instead of keeping every one for the life of
  the game connection, which grew memory for as long as the logger ran.
- Bounded packet queues and payload reassembly by size, fragment count, and
  timeout.
- Wrote exports to a temporary file and published them only when complete, and
  neutralized formula-leading member names in CSV exports.
- Shut the proxy down when the window process exits unexpectedly, and started
  with default options when `gfl2logger.config.yaml` is unreadable.
- Updated mitmproxy to 12.2.3.

The capture path on Windows is unchanged from v0.2.5. This build was verified
by automated tests, packaging, and a window start-up check on Windows, and has
not yet been run against a live game session. Please report any problems.

### macOS, since v0.1.2

- Renamed the app from `gf2logger.app` to `gfl2logger.app` to match the
  project. Replace the old app with the new one; exports and settings stay in
  `~/gfl2logger`.
- No functional changes. The version number moves to v0.3.0 to match Windows.

### Both

- Every change is now tested and built on Windows and macOS, and a release
  publishes both platforms together.

## Installation

**Windows:** download the `.exe`, place it in a folder you can write to, and
run it. If SmartScreen shows **Windows protected your PC**, choose **More
info > Run anyway**. Allow the administrator prompt for mitmproxy's traffic
redirector if Windows shows one.

**macOS:** open the `.dmg` and drag `gfl2logger.app` to **Applications**, or
unzip the `.zip`. The application remains ad-hoc signed and is not yet
Developer ID-notarized. If macOS blocks the first launch, follow the **Open
Anyway** instructions in the [README](../../#macos). Approve **Mitmproxy
Redirector** when macOS requests Network Extension permission.

Start `gfl2logger` before the game on either platform.
