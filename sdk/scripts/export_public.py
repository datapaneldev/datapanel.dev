"""Build a clean customer bundle without Git history or internal reports."""

import argparse
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_ROOT_FILES = {
    "README.md",
    "README.zh-CN.md",
    "LICENSE",
    "pyproject.toml",
    "CONTRIBUTING.md",
    "SECURITY.md",
    ".env.example",
    ".gitignore",
    "requirements-lock.txt",
}
ALLOWED_DIRS = {"docs", "src", "examples", ".agents", "tests", "scripts", ".github"}
EXCLUDED_PARTS = {"__pycache__", "work", "build", "dist", ".git"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    subprocess.run([sys.executable, str(ROOT / "scripts/check_repository.py")], check=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.output, "x", compression=zipfile.ZIP_DEFLATED) as bundle:
        for path in sorted(ROOT.rglob("*")):
            relative = path.relative_to(ROOT)
            if not path.is_file() or path.is_symlink():
                continue
            if EXCLUDED_PARTS.intersection(relative.parts):
                continue
            if any(part.endswith(".egg-info") for part in relative.parts):
                continue
            if relative.parts[0] not in ALLOWED_DIRS and str(relative) not in ALLOWED_ROOT_FILES:
                continue
            if path.suffix in {".pyc", ".key", ".pem"}:
                continue
            bundle.write(path, str(Path("datapanel-agent-examples") / relative))
    print(f"Customer bundle: {args.output}")


if __name__ == "__main__":
    main()
