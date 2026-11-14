# UltraRustDesk changelog

Decisions and problems that the Git history does not explain well.

## 2026-11-14_233647_1794695807

- Based on the PR 17059 branch (`codex/confirm-saved-password-connections`),
  which sits one commit on top of upstream `master` `fc9713c1`.
- The confirmation option was renamed from `allow-confirm-saved-password` to
  `enable-confirm-saved-password`: `allow-` options default to off and
  `enable-` options default to on, so the rename makes it on by default without
  new default-value code.
- The app name is set in the main crate (`init_app_name`, called from
  `core_main`, `load_custom_client` and Android `startServer`) instead of
  changing `APP_NAME`'s default in `libs/hbb_common`, which is a submodule of
  rustdesk/hbb_common. Config file names derive from `APP_NAME` and are cached
  on first read, so every process entry point sets it before touching config;
  Android's `startServer` can run at boot before Flutter starts.
- A non-RustDesk app name makes RustDesk treat the build as a custom client.
  That turns off update checks (wanted: they would offer official RustDesk) and
  makes Windows install the exe as `UltraRustDesk.exe`.
- Linux keeps the name RustDesk: Linux code looks up the systemd unit, process
  and desktop file by the lowercase app name, and all Linux packaging hard-codes
  `rustdesk`.
- The icon recolor rotates blue/cyan hues by -75 degrees and darkens saturated
  pixels by 20 %; `.ico` files keep their BMP or PNG entry encoding because the
  tray code decodes `res/tray-icon.ico` with the `image` crate.
- Upstream's iOS job built an `.ipa` but published nothing; the workflow now
  wraps the archived app into an unsigned `.ipa` and publishes it.
- The MSI is packaged with `--app-name UltraRustDesk` (exe renamed in a copy of
  the dist), and the portable packer gets `UltraRustDesk.exe` as its payload so
  it extracts to its own folder.
