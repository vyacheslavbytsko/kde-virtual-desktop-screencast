#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-or-later
set -euo pipefail

case ${1:-} in
    kwin|xdg-desktop-portal-kde) package=$1 ;;
    *) echo 'Choose kwin or xdg-desktop-portal-kde.' >&2; exit 1 ;;
esac

readarray -t sources < <(find build/copr-srpms -maxdepth 1 -name "$package-*.src.rpm")
if [[ ${#sources[@]} != 1 ]]; then
    echo "Expected one source RPM for $package." >&2
    exit 1
fi

source=${sources[0]}
dnf -y --setopt=install_weak_deps=False builddep "$source"
top=$(realpath -m "build/rpmbuild-$package")
mkdir -p "$top" build/binary
rpmbuild --rebuild --define "_topdir $top" --define '_smp_build_ncpus 3' "$source"

for rpm in "$top"/RPMS/x86_64/*.rpm; do
    name=$(rpm -qp --qf '%{NAME}' "$rpm")
    case $name in
        kwin|kwin-common|kwin-libs|xdg-desktop-portal-kde) cp "$rpm" build/binary/ ;;
    esac
done
