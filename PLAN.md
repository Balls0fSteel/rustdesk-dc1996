# UltraRustDesk plan

See `ultrarustdesk/README.md` for what this fork changes.

## Current work

2026-11-14_233647_1794695807
- Branch `ultrarustdesk`: confirmation before saved-password connections (from
  rustdesk/rustdesk PR 17059, now on by default), UltraRustDesk name, green
  icons, and the `UltraRustDesk Build` workflow.
- First CI run of `.github/workflows/ultrarustdesk.yml` still to do; then
  smoke-test the Windows exe/msi and the Android APK on real devices.

## Next steps

- Stable Android signing: create a keystore and add the `ANDROID_*` secrets so
  APK updates install over each other.
- Linux rename: deb (`build.py`, `res/DEBIAN/*`), rpm specs, PKGBUILD,
  AppImage, Flatpak and `res/rustdesk.service` all use `rustdesk` names; then
  drop the Linux exception in `init_app_name`.
- Optional: green UI accent color (`MyTheme.accent` in `flutter/lib/common.dart`,
  Android `primary` color) to match the icon.
- Optional: own macOS/iOS bundle identifiers.

## Open questions

- Should the confirmation also cover connections without a saved password
  (for example peers in click-to-approve mode)?
