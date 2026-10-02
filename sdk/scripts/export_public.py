"""Export checked immutable bytes without Git history, secrets or archives."""

import argparse
import subprocess
import sys
import zipfile
from pathlib import Path

from publication_policy import collect

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    subprocess.run([sys.executable, str(ROOT / "scripts/check_repository.py")], check=True)
    # Validate the bytes we actually write, rather than rescanning and reopening files later.
    files = collect(ROOT)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.output, "x", compression=zipfile.ZIP_DEFLATED) as bundle:
        for relative, data in files.items():
            bundle.writestr(str(Path("datapanel-agent-examples") / relative), data)
    print(f"Customer bundle: {args.output}")


if __name__ == "__main__":
    main()
