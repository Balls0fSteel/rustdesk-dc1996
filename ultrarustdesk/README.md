# UltraRustDesk

UltraRustDesk is a rebranded RustDesk build with one extra feature: it asks
for confirmation before connecting to a device with a saved password. It is
built from the `ultrarustdesk` branch.

## What differs from RustDesk

- **Confirmation before connecting.** When you open a session to a device
  whose password is saved (locally or in the address book), a dialog shows the
  device's alias and ID with **Cancel** and **Connect**. This is on by default;
  turn it off under Settings > General, "Confirm before connecting with saved
  passwords" (mobile: Settings). Reconnects, side switches and "Request
  approval" logins do not ask. Option key: `enable-confirm-saved-password`.
- **Name.** The app calls itself UltraRustDesk on Windows, Android, macOS and
  iOS (`init_app_name` in `src/common.rs`). Config files, the Windows service,
  install folder (`C:\Program Files\UltraRustDesk`), URI scheme
  (`ultrarustdesk://`) and the Android package (`com.ultrarustdesk.client`)
  are separate from RustDesk's, so both can be installed side by side. It
  connects to the same RustDesk servers and peers as RustDesk.
- **Green icon.** All app, tray, installer and launcher icons are recolored by
  `ultrarustdesk/recolor_icons.py`.
- **No update prompts.** A non-RustDesk name turns off RustDesk's update check,
  so the app never offers to replace itself with official RustDesk.

## Building

Run the **UltraRustDesk Build** workflow (`.github/workflows/ultrarustdesk.yml`)
from the Actions tab, or:

```sh
gh workflow run ultrarustdesk.yml --ref ultrarustdesk
```

It recreates the `ultrarustdesk-nightly` pre-release at the built commit, runs
the upstream `flutter-build.yml` for every platform, and renames the assets to
`ultrarustdesk-*`. A full run takes a few hours.

## Known limits

- **Linux** keeps the internal name RustDesk: the deb, rpm, AppImage and
  Flatpak packaging and the systemd unit use `rustdesk` names that the Linux
  code looks up by app name. Linux builds get the green icon and the
  confirmation, but they install as `rustdesk` and replace an official RustDesk
  package.
- **Signing.** Without signing secrets in the repository:
  - Windows binaries are unsigned (SmartScreen warns on first run).
  - Android APKs are signed with the CI runner's throwaway debug key, so each
    build has a different signature: uninstall before installing a newer one.
    Add `ANDROID_SIGNING_KEY`, `ANDROID_ALIAS`, `ANDROID_KEY_STORE_PASSWORD`
    and `ANDROID_KEY_PASSWORD` secrets to get stable signing.
  - macOS builds are not signed or notarized.
  - The iOS `.ipa` is unsigned and must be signed while sideloading.
- The macOS and iOS bundle identifiers are unchanged.
- The `RustDesk` text inside translations is replaced with UltraRustDesk at
  runtime, except "Powered by RustDesk".

## Merging upstream

Merge `rustdesk/rustdesk` `master` into this branch. If upstream changes any
icon, take theirs and re-run the recolor script on the new blue icons only;
running it twice shifts the colors again:

```sh
python ultrarustdesk/recolor_icons.py
```
