"""Build and verify an allowlisted skill ZIP and its SHA-256 checksum."""

import argparse
import hashlib
from pathlib import Path
import sys
import tempfile
import zipfile

from validate_skill import PACKAGE_FILES, validate


def build(root, output):
    root = root.resolve()
    output = output.resolve()
    name = validate(root)
    if output in {root / path for path in PACKAGE_FILES}:
        raise ValueError("The archive output cannot overwrite a package source file")
    payload = {f"{name}/{path}": (root / path).read_bytes() for path in PACKAGE_FILES}
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=output.parent, suffix=".zip", delete=False) as temporary:
        temporary_path = Path(temporary.name)
    try:
        with zipfile.ZipFile(temporary_path, "w") as archive:
            for path, content in sorted(payload.items()):
                entry = zipfile.ZipInfo(path, date_time=(1980, 1, 1, 0, 0, 0))
                entry.create_system = 3
                entry.external_attr = 0o100644 << 16
                archive.writestr(entry, content, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
        with zipfile.ZipFile(temporary_path) as archive:
            if archive.testzip() is not None or set(archive.namelist()) != set(payload):
                raise ValueError("Archive integrity or file inventory mismatch")
            for path, content in payload.items():
                if archive.read(path) != content:
                    raise ValueError(f"Archive content mismatch: {path}")
        temporary_path.replace(output)
    finally:
        temporary_path.unlink(missing_ok=True)
    checksum = hashlib.sha256(output.read_bytes()).hexdigest()
    output.with_suffix(output.suffix + ".sha256").write_text(f"{checksum}  {output.name}\n")
    return checksum


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, default=Path("dist/cult-like-launch.zip"))
    args = parser.parse_args()
    try:
        checksum = build(args.root, args.output)
    except (ValueError, OSError, zipfile.BadZipFile) as error:
        print(f"Build failed: {error}", file=sys.stderr)
        return 1
    print(f"Built and verified {args.output} ({len(PACKAGE_FILES)} files)")
    print(f"SHA-256: {checksum}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
