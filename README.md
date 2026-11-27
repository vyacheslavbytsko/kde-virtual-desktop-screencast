# KDE virtual desktop screencast

Share a single KDE Plasma virtual desktop on Wayland. Choose a desktop and monitor in the system screen-sharing dialog. The stream stays on that desktop when you switch desktops locally.

The stream shows the Plasma wallpaper, windows, and dialogs on the selected desktop, plus a task panel with icons for open and minimized windows. Plasma panel widgets are outside the capture. If the application requests a cursor, it appears while the shared desktop is active on the selected monitor.

## Install on Fedora 45 x86_64

These experimental packages target KDE Plasma 6.8.3. The signed [DNF repository](https://vyacheslavbytsko.github.io/kde-virtual-desktop-screencast/) provides `kwin`, `kwin-common`, `kwin-libs`, and `xdg-desktop-portal-kde`.

1. Download [kde-virtual-desktop.repo](https://vyacheslavbytsko.github.io/kde-virtual-desktop-screencast/kde-virtual-desktop.repo) and run this command from the download directory.

   ```bash
   sudo dnf config-manager addrepo --from-repofile=./kde-virtual-desktop.repo
   ```

2. Exclude these four packages from Fedora's `fedora` and `updates` repositories so DNF gets them from the patched repository. If those repositories already have exclusions, append the four package names to each list. Otherwise, run the following command.

   ```bash
   sudo dnf config-manager setopt \
     fedora.excludepkgs=kwin,kwin-common,kwin-libs,xdg-desktop-portal-kde \
     updates.excludepkgs=kwin,kwin-common,kwin-libs,xdg-desktop-portal-kde
   ```

   If you use `updates-testing`, add the same exclusions there.

3. Run `sudo dnf upgrade --refresh`. If prompted to import the signing key, check that its fingerprint is `7272 6946 C328 DA0A BAB9 9479 6097 318B DD2B 6A3E`. Log out of Plasma and log back in to start sharing.

## Licenses

The KWin, KDE Portal, and Plasma Wayland Protocols patches follow the SPDX license headers of the files they modify. See [LICENSES](LICENSES/). The build script and HTML test page are available under GPL-2.0-or-later.
