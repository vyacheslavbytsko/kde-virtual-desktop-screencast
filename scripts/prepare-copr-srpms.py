#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
import argparse
import re
import shutil
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = "zkde-screencast-unstable-v1.xml"
FEATURE = "kwin-vdesktop-screencast"


def rpm_query(source, format):
    return subprocess.check_output(
        ["rpm", "-qp", "--queryformat", format, source], text=True
    )


def replace_once(text, pattern, replacement):
    updated, matches = re.subn(pattern, replacement, text, flags=re.MULTILINE)
    if matches != 1:
        raise ValueError(f"Expected one spec match for {pattern}, found {matches}")
    return updated


def build_srpm(source, name, revision, out):
    subprocess.run(["rpm", "-K", "--nosignature", source], check=True)
    package, version = rpm_query(source, r"%{NAME} %{VERSION}").split()
    if package != name or rpm_query(source, "%{SOURCEPACKAGE}") != "1":
        raise ValueError(f"Expected an official Fedora source RPM for {name}: {source}")

    patch = f"{name}-{version}-virtual-desktop-v4.patch"
    protocol_patch = "plasma-wayland-protocols-virtual-desktop-v4.patch"
    cmake_dir = "src/wayland" if name == "kwin" else "src"

    with TemporaryDirectory(prefix=f"vdesktop-{name}-") as directory:
        top = Path(directory)
        sources = top / "SOURCES"
        sources.mkdir()
        with subprocess.Popen(["rpm2cpio", source], stdout=subprocess.PIPE) as archive:
            subprocess.run(
                ["cpio", "--extract", "--make-directories", "--quiet", "--no-absolute-filenames"],
                cwd=sources, stdin=archive.stdout, check=True,
            )
            if archive.wait():
                raise ValueError(f"Could not unpack {source}")

        spec_file = sources / f"{name}.spec"
        spec = spec_file.read_text()
        spec = replace_once(
            spec, r"^(Release:[ \t]*[0-9]+)(%\{\?dist\})[ \t]*$",
            rf"\g<1>.{revision}\g<2>.vdesktop",
        )
        feature = f"Provides: {FEATURE} = 4" if name == "kwin" else f"Requires: {FEATURE} = 4"
        spec = replace_once(
            spec, r"^(Source0:[^\n]*)$",
            rf"\g<1>\nPatch900: {patch}\nSource910: {protocol_patch}\n{feature}",
        )
        spec = replace_once(
            spec, r"^%autosetup -p1[ \t]*$",
            lambda match: match[0] + f"""
# Build both components against the same patched protocol, using a private copy.
test -f {cmake_dir}/CMakeLists.txt
grep -Fq '${{PLASMA_WAYLAND_PROTOCOLS_DIR}}/{PROTOCOL}' {cmake_dir}/CMakeLists.txt
cp %{{_datadir}}/plasma-wayland-protocols/{PROTOCOL} {cmake_dir}/{PROTOCOL}
patch --batch --forward --fuzz=0 {cmake_dir}/{PROTOCOL} %{{SOURCE910}}
sed -i 's|${{PLASMA_WAYLAND_PROTOCOLS_DIR}}/{PROTOCOL}|${{CMAKE_CURRENT_SOURCE_DIR}}/{PROTOCOL}|' {cmake_dir}/CMakeLists.txt
""".rstrip(),
        )
        spec_file.write_text(spec)
        for filename in (patch, protocol_patch):
            shutil.copyfile(ROOT / "patches" / filename, sources / filename)
        subprocess.run(
            ["rpmbuild", "-bs", "--nodeps", "--define", f"_topdir {top}",
             "--define", f"_srcrpmdir {out}", spec_file],
            check=True,
        )


def main():
    parser = argparse.ArgumentParser(description="Prepare two v4 source RPMs for Fedora 45 Copr.")
    parser.add_argument("kwin", type=Path)
    parser.add_argument("portal", type=Path)
    parser.add_argument("--revision", type=int, default=5)
    parser.add_argument("--output", type=Path, default=Path("build/copr-srpms"))
    args = parser.parse_args()
    if args.revision < 1:
        parser.error("--revision must be positive")
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    for path, name in ((args.kwin, "kwin"), (args.portal, "xdg-desktop-portal-kde")):
        build_srpm(path.resolve(), name, args.revision, out)


if __name__ == "__main__":
    main()
