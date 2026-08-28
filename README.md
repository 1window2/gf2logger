# gfl2logger for macOS

> [!IMPORTANT]
> This repository is a macOS-only fork of
> [blead/gfl2logger](https://github.com/blead/gfl2logger). Windows users should
> download and use the [original Windows version](https://github.com/blead/gfl2logger/releases).

`gfl2logger` captures Girls' Frontline 2: Exilium network payloads and exports
platoon-management data to local CSV and JSON files. This fork supports the
iPhone/iPad App Store version of GF2 running on an Apple-silicon Mac.

## Requirements

- An Apple-silicon Mac
- The iPhone/iPad version of Girls' Frontline 2: Exilium installed from the Mac
  App Store
- Permission to enable the bundled Mitmproxy Redirector Network Extension

## Installation

1. Download `gf2logger-v0.1.0-macos-arm64.zip` or
   `gf2logger-v0.1.0-macos-arm64.dmg` from
   [Releases](https://github.com/1window2/gf2logger/releases).
2. For the ZIP, unzip it and Control-click `gf2logger.app`. For the DMG, open
   it, drag `gf2logger.app` to **Applications**, and Control-click the installed
   app.
3. Choose **Open**, then confirm **Open** in the Gatekeeper dialog.
4. Approve **Mitmproxy Redirector** when macOS requests Network Extension
   permission.

If the redirector is not enabled automatically, open **System Settings >
General > Login Items & Extensions > Network Extensions**, enable **Mitmproxy
Redirector**, and relaunch `gfl2logger`.

The application itself is currently ad-hoc signed rather than Developer
ID-signed and notarized. Its bundled network redirector is separately signed
and notarized by the mitmproxy project.

## Usage

1. Start `gfl2logger` before GF2. If GF2 is already running, restart it after
   the logger is ready.
2. Leave the desired payload checkboxes enabled.
3. Start GF2 and open its Platoon pages to request the relevant data.

Exports and `gfl2logger.config.yaml` are written to `~/gfl2logger`.

The checkboxes are organized into two groups:

- **Platoon:** Platoon Profile, Members, Activity, Updates
- **Others:** Weapons, Attachments, Common Keys, Formations

### Exported Data

| Option | Payload | Description | Format |
| --- | ---: | --- | --- |
| Platoon Profile | `21905` | Platoon identity, level, member count, announcements, and recruitment settings | JSON |
| Members | `21917` | Member names, levels, contributions, scores, and login times | CSV |
| Activity | `21935` | Platoon objectives and recent member activity | JSON |
| Updates | `21960` | Live platoon update messages, preserved by protobuf field number and as lossless raw hex | JSON |
| Weapons | `11021` | Weapons owned by the current account | CSV |
| Attachments | `11061` | Attachments owned by the current account | CSV |
| Common Keys | `11138` | Common Keys owned by the current account | CSV |
| Formations | `23201` | Saved formations | JSON |

The Profile, Members, and Activity payloads have been validated against the
App Store client on macOS. Updates are captured losslessly, but semantic field
names will require a live `21960` sample because that server-push payload was
not emitted during validation.

## How It Works

Mitmproxy's local capture mode restricts interception to the GF2 executable,
`SnqxExilium`. The logger reads server-to-client payloads without initiating or
modifying game connections. TLS connections are passed through without
decryption, so no mitmproxy certificate needs to be installed.

## Build from Source

The project uses [PDM](https://pdm-project.org/) and Python 3.13:

```sh
git clone https://github.com/1window2/gf2logger.git
cd gf2logger
pdm install
pdm run pyinstaller
```

The Apple-silicon build is created at `dist/gf2logger.app`. To run directly
from source:

```sh
pdm run protoc
pdm run python main.py
```

## Credits

The packet parser, data exporters, and original Windows application were
created by [blead](https://github.com/blead) in
[blead/gfl2logger](https://github.com/blead/gfl2logger). This fork adds the
macOS capture path, packaging, platform-specific UI fixes, and expanded platoon
payload support.

## License

This project retains the original MIT license. See [LICENSE](LICENSE).
