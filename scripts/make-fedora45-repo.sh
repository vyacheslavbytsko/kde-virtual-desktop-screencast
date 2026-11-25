#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-or-later
set -euo pipefail
umask 077
: "${RPM_SIGNING_KEY:?Missing RPM_SIGNING_KEY GitHub Actions secret}"
: "${RPM_SIGNING_FINGERPRINT:?Missing RPM_SIGNING_FINGERPRINT GitHub Actions variable}"

rpm_directory=$1
site=$2
base_url=${3%/}
repository="$site/fedora/45/x86_64"
mkdir -p "$repository"

export GNUPGHOME
GNUPGHOME=$(mktemp -d)
trap 'gpgconf --kill all; rm -rf "$GNUPGHOME"' EXIT
printf '%s\n' "$RPM_SIGNING_KEY" | gpg --batch --import
unset RPM_SIGNING_KEY
gpg --batch --list-secret-keys "$RPM_SIGNING_FINGERPRINT" >/dev/null
gpg --batch --armor --export "$RPM_SIGNING_FINGERPRINT" > "$site/rpm-signing-key.asc"
test -s "$site/rpm-signing-key.asc"

for rpm in "$rpm_directory"/*.rpm; do
    cp "$rpm" "$repository/"
done
rpmsign --define '_openpgp_sign gpg' --key-id "$RPM_SIGNING_FINGERPRINT" --addsign "$repository"/*.rpm
createrepo_c "$repository"
gpg --batch --local-user "$RPM_SIGNING_FINGERPRINT" --armor --detach-sign "$repository/repodata/repomd.xml"

# GitHub Pages uses default web permissions on uploaded files.
chmod -R a+rX "$site"
cat > "$site/kde-virtual-desktop.repo" <<REPO
[kde-virtual-desktop]
name=KDE virtual desktop screencast for Fedora 45
baseurl=$base_url/fedora/45/\$basearch/
enabled=1
pkg_gpgcheck=1
repo_gpgcheck=1
gpgkey=$base_url/rpm-signing-key.asc
includepkgs=kwin,kwin-common,kwin-libs,xdg-desktop-portal-kde
REPO
chmod a+r "$site/kde-virtual-desktop.repo"
cat > "$site/index.html" <<'HTML'
<!doctype html>
<meta charset="utf-8">
<title>KDE virtual desktop screencast</title>
<h1>KDE virtual desktop screencast</h1>
<p>RPM repository for Fedora 45 x86_64.</p>
<ul>
  <li><a href="kde-virtual-desktop.repo">DNF repository configuration</a></li>
  <li><a href="rpm-signing-key.asc">OpenPGP public signing key</a></li>
</ul>
HTML
chmod a+r "$site/index.html"
