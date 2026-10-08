# gfl2logger for macOS v0.1.2

This patch release fixes lost captures, unbounded memory growth during long
sessions, and several ways the app could keep running without a window.
Updating from v0.1.1 is recommended.

## Fixes

- Kept message bytes that arrive split across TCP chunks, and finished parsing
  data already received when a connection closes, so responses are no longer
  dropped or misread at chunk boundaries.
- Released forwarded TCP messages instead of keeping every one for the life of
  the game connection, which grew memory for as long as the logger ran.
- Wrote CSV and JSON exports to a temporary file and published them only when
  complete, so a malformed response can no longer leave a truncated file.
  Responses with no entries now export an empty table instead of failing.
- Shut the proxy down when the window process exits unexpectedly, and closed
  the window when the proxy is gone, instead of leaving a hidden process
  capturing in the background.
- Started with default options when `gfl2logger.config.yaml` is unreadable
  rather than failing to open, and kept the window able to quit after a failed
  **Save config**.
- Shortened the log entry for a malformed payload, which previously printed
  the entire message in hexadecimal.

## Installation

Download `gf2logger-v0.1.2-macos-arm64.zip` for the portable app, or
`gf2logger-v0.1.2-macos-arm64.dmg` for drag-and-drop installation. Start
`gf2logger` before GF2.

The application remains ad-hoc signed and is not yet Developer ID-notarized. If
macOS blocks the first launch, follow the **Open Anyway** instructions in the
[README](https://github.com/1window2/gf2logger#notice).
