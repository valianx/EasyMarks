"""Build runtime files and their license; does not install or publish anything."""
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "addon" / "EasyMarks"
RUNTIME_FILES = ("Errors.lua", "Domain/Markers.lua", "UI/Wheel.lua", "Core.lua")
FILES = ("EasyMarks.toc", *RUNTIME_FILES, "Bindings.xml", "LICENSE")


def source_file(name):
    return ROOT / name if name == "LICENSE" else SOURCE / name


def read_version():
    toc = (SOURCE / FILES[0]).read_text(encoding="utf-8")
    version_match = re.search(r"^## Version: ([a-zA-Z0-9.-]+)$", toc, re.MULTILINE)
    if not version_match:
        raise ValueError("Missing or invalid version in EasyMarks.toc")
    return version_match.group(1)


def verify_archive(destination):
    with ZipFile(destination) as archive:
        if archive.namelist() != [f"EasyMarks/{name}" for name in FILES]:
            raise ValueError("Unexpected files or layout in addon ZIP")
        if archive.testzip() is not None:
            raise ValueError("Corrupt addon ZIP")
        for name in FILES:
            if archive.read(f"EasyMarks/{name}") != source_file(name).read_bytes():
                raise ValueError(f"Packaged file differs from source: {name}")


def main():
    version = read_version()
    toc = (SOURCE / FILES[0]).read_text(encoding="utf-8")
    runtime = [line.strip() for line in toc.splitlines() if line.strip() and not line.startswith("#")]
    if runtime != list(RUNTIME_FILES):
        raise ValueError("Update the packaging allowlist to match the TOC")
    ET.parse(SOURCE / "Bindings.xml")
    for name in FILES:
        if not source_file(name).is_file():
            raise FileNotFoundError(name)

    destination = ROOT / "dist" / f"EasyMarks-{version}.zip"
    destination.parent.mkdir(exist_ok=True)
    with ZipFile(destination, "w", ZIP_DEFLATED) as archive:
        for name in FILES:
            archive.write(source_file(name), f"EasyMarks/{name}")
    verify_archive(destination)
    print(f"Verified: {destination}")
    return destination


if __name__ == "__main__":
    main()
