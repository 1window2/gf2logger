# gfl2logger for macOS v0.1.1

This patch release addresses three security findings. Updating from v0.1.0 is
recommended.

## Security fixes

- Bounded packet queues and payload reassembly by size, fragment count, and
  timeout to prevent type-zero payload sequences from exhausting memory.
- Neutralized formula-leading platoon member names in CSV exports so spreadsheet
  applications treat them as text.
- Restricted release publishing to version-tag pushes and disabled release asset
  overwrites.

## Installation

Download `gf2logger-v0.1.1-macos-arm64.zip` for the portable app, or
`gf2logger-v0.1.1-macos-arm64.dmg` for drag-and-drop installation. Start
`gf2logger` before GF2.

The application remains ad-hoc signed and is not yet Developer ID-notarized. If
macOS blocks the first launch, follow the **Open Anyway** instructions in the
[README](https://github.com/1window2/gf2logger#notice).
