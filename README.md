# KDE virtual desktop screencast

An experimental build for Fedora 45 x86_64 and KDE Plasma 6.8.3 on Wayland. In the system screen-sharing dialog, select a virtual desktop and a monitor. The stream keeps showing the selected desktop when you switch desktops locally.

The stream captures the Plasma wallpaper, windows, and dialogs on the selected desktop. Its task panel shows icons for open and minimized windows on that desktop. If the application requests a cursor, KWin includes it while the selected desktop is active on the selected monitor. Plasma panel widgets are outside the captured content.

## Updates for Fedora 45 x86_64

GitHub Actions builds patched versions of `kwin`, `kwin-common`, `kwin-libs`, and `xdg-desktop-portal-kde`, checks that they install together in a container, and publishes a signed repository on [GitHub Pages](https://vyacheslavbytsko.github.io/kde-virtual-desktop-screencast/). Both source packages use the same patched Wayland XML protocol at build time. PipeWire and the system protocol packages can be updated through Fedora as usual.

1. Download [kde-virtual-desktop.repo](https://vyacheslavbytsko.github.io/kde-virtual-desktop-screencast/kde-virtual-desktop.repo) and run the following command from the download directory.

   ```bash
   sudo dnf config-manager addrepo --from-repofile=./kde-virtual-desktop.repo
   ```

2. Exclude the four packages from the standard Fedora repositories so DNF gets them from the patched repository. If you have no existing exclusions in `fedora` or `updates`, use the following command.

   ```bash
   sudo dnf config-manager setopt \
     fedora.excludepkgs=kwin,kwin-common,kwin-libs,xdg-desktop-portal-kde \
     updates.excludepkgs=kwin,kwin-common,kwin-libs,xdg-desktop-portal-kde
   ```

   If you already have exclusions, append these package names to your existing lists. Add them to `updates-testing` as well if that repository is enabled.

3. Run `sudo dnf upgrade --refresh`. When DNF prompts you to import the signing key, compare its fingerprint with `RPM_SIGNING_FINGERPRINT` in the repository's Actions settings. After updating, log out of Plasma and log back in.

### Publishing an update

GitHub Actions checks the stable Fedora 45 repositories daily. When Fedora publishes a newer revision and patches are available for both source package versions, the workflow updates `packaging/fedora/upstream-srpms.sha256` with the source RPM names and checksums and starts a build. If patches are missing for a new Plasma release, the check stops. Once the patches have been ported, you can run the check manually.

Changes to the build inputs on `main` also trigger a build. You can start one manually under **Actions → Fedora 45 RPM repository**. To republish the same Fedora revision, increase the `--revision` value in the package preparation script. If the build or installation check fails, GitHub Pages continues serving the previous release.

Publishing uses **Settings → Pages → GitHub Actions**, the `RPM_SIGNING_KEY` Actions secret containing the OpenPGP private key, and the `RPM_SIGNING_FINGERPRINT` Actions variable containing its full fingerprint. The container check verifies that the RPMs install together. Test virtual desktop capture in a Plasma session.

## Authors

- [vyacheslavbytsko](https://github.com/vyacheslavbytsko), project lead and Plasma testing.
- OpenAI Codex, patch implementation, RPM packaging, and GitHub Actions.

## Sources and licenses

The patches apply to [KWin](https://invent.kde.org/plasma/kwin/-/tree/v6.8.3), [KDE Portal](https://invent.kde.org/plasma/xdg-desktop-portal-kde/-/tree/v6.8.3), and Plasma Wayland Protocols 1.23.0. Changes to source files are distributed under the licenses identified by their SPDX headers. The license texts are in `LICENSES/`.

Packaging recipes come from the Fedora Koji source RPMs listed in `packaging/fedora/upstream-srpms.sha256`. The build script and HTML test page are available under GPL-2.0-or-later.
