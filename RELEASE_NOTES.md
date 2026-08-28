# gfl2logger for macOS v0.1.0

This is the first macOS release of `1window2/gfl2logger`. It is a macOS-only
fork of [blead/gfl2logger](https://github.com/blead/gfl2logger), based on the
original project's [v0.2.5 release](https://github.com/blead/gfl2logger/releases/tag/v0.2.5).
Windows users should continue to use the original project.

## Highlights

- Native process-local capture of the App Store GF2 client (`SnqxExilium`) on
  Apple-silicon Macs
- Platoon Profile (`21905`), Members (`21917`), Activity (`21935`), and Updates
  (`21960`) capture
- Centered **Platoon** and **Others** groups for the eight payload options
- CSV and JSON output under `~/gfl2logger`
- Bundled, signed, and notarized Mitmproxy Redirector Network Extension
- ARM64 `.app` packaging and macOS release automation

Profile, Members, and Activity decoding were validated against live GF2
traffic. Updates are captured losslessly by protobuf field number and raw hex;
semantic names can be added after a live `21960` server-push sample is observed.

## Installation

Download `gf2logger-v0.1.0-macos-arm64.zip`, unzip it, then Control-click
`gf2logger.app` and choose **Open**. Alternatively, open
`gf2logger-v0.1.0-macos-arm64.dmg`, drag `gf2logger.app` to **Applications**,
and open it there. Approve **Mitmproxy Redirector** when
macOS requests Network Extension permission. Start the logger before starting
GF2.

The application is ad-hoc signed and is not yet Developer ID-notarized, so the
first launch requires the Control-click **Open** flow.
