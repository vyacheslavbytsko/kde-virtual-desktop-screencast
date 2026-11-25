#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-or-later
set -euo pipefail

manifest=$(realpath "$(dirname "${BASH_SOURCE[0]}")/../packaging/fedora/upstream-srpms.sha256")
mkdir -p "${1:-build/upstream}"
cd "${1:-build/upstream}"

while read -r checksum filename; do
    if [[ $filename =~ ^(kwin|xdg-desktop-portal-kde)-([0-9]+\.[0-9]+\.[0-9]+)-([0-9]+\.fc45)\.src\.rpm$ ]]; then
        package=${BASH_REMATCH[1]}
        version=${BASH_REMATCH[2]}
        release=${BASH_REMATCH[3]}
    else
        echo "Unexpected Fedora SRPM name: $filename" >&2
        exit 1
    fi
    if ! printf '%s  %s\n' "$checksum" "$filename" | sha256sum --check --status; then
        curl -fsSL --retry 3 --output "$filename" \
            "https://kojipkgs.fedoraproject.org/packages/$package/$version/$release/src/$filename"
    fi
done < "$manifest"

sha256sum --check --strict "$manifest"
