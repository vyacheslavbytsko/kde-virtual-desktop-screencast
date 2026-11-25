#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
import hashlib
import re
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import rpm

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "packaging/fedora/upstream-srpms.sha256"
SOURCE_NAME = re.compile(
    r"(kwin|xdg-desktop-portal-kde)-(\d+\.\d+\.\d+)-(\d+\.fc45)\.src\.rpm"
)
PACKAGES = ("kwin", "xdg-desktop-portal-kde")


def source_parts(filename):
    match = SOURCE_NAME.fullmatch(filename)
    if match is None:
        raise ValueError(f"Unexpected Fedora 45 source package: {filename}")
    return match.groups()


def select_sources(filenames):
    selected = {}
    for filename in set(filenames):
        name, version, release = source_parts(filename)
        if name in selected:
            raise ValueError(f"Multiple source versions reported for {name}")
        selected[name] = (filename, version, release)
    if set(selected) != set(PACKAGES):
        raise ValueError("Need both KWin and KDE Portal from Fedora's stable repositories")
    return selected


def main():
    known_hashes = {
        filename: checksum
        for checksum, filename in (line.split() for line in MANIFEST.read_text().splitlines())
    }
    previous = select_sources(known_hashes)
    candidates = select_sources(sys.stdin.read().split())

    for name, (filename, version, release) in candidates.items():
        _, old_version, old_release = previous[name]
        if rpm.labelCompare(("0", version, release), ("0", old_version, old_release)) < 0:
            raise ValueError(f"Fedora mirror is older than the recorded revision: {filename}")
        if not (ROOT / "patches" / f"{name}-{version}-virtual-desktop-v4.patch").is_file():
            raise ValueError(f"{filename} needs a v4 patch before this version can be built")
    versions = {version for _, version, _ in candidates.values()}
    if len(versions) != 1:
        raise ValueError("Waiting for matching Plasma versions in Fedora's stable repositories")

    lines = []
    with TemporaryDirectory(prefix="fedora45-srpms-") as directory:
        for name in PACKAGES:
            filename, version, release = candidates[name]
            checksum = known_hashes.get(filename)
            if checksum is None:
                source = Path(directory) / filename
                url = f"https://kojipkgs.fedoraproject.org/packages/{name}/{version}/{release}/src/{filename}"
                subprocess.run(["curl", "-fsSL", "--retry", "3", "-o", source, url], check=True)
                subprocess.run(["rpm", "-K", "--nosignature", source], check=True)
                identity = subprocess.check_output(
                    ["rpm", "-qp", "--qf", "%{NAME} %{VERSION} %{RELEASE} %{SOURCEPACKAGE}", source],
                    text=True,
                )
                if identity != f"{name} {version} {release} 1":
                    raise ValueError(f"Source RPM identity does not match {filename}")
                with source.open("rb") as stream:
                    checksum = hashlib.file_digest(stream, "sha256").hexdigest()
            lines.append(f"{checksum}  {filename}\n")

    updated = "".join(lines)
    if MANIFEST.read_text() != updated:
        MANIFEST.write_text(updated)


if __name__ == "__main__":
    main()
