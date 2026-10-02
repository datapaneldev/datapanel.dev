"""Check the exact public package surface and local documentation links."""

import re
from pathlib import Path
from urllib.parse import unquote

from publication_policy import collect


def main():
    root = Path(__file__).resolve().parents[1]
    try:
        files = collect(root)
    except ValueError as error:
        print(error)
        return 1
    errors = []
    for relative, data in files.items():
        if relative.suffix != ".md":
            continue
        for target in re.findall(r"\]\(([^)]+)\)", data.decode("utf-8")):
            if "://" in target or target.startswith(("#", "mailto:")):
                continue
            target = unquote(target.split("#")[0])
            resolved = (root / relative.parent / target).resolve()
            if not resolved.is_relative_to(root.resolve()) or not resolved.exists():
                errors.append(f"Broken or escaping link: {relative}")
    for error in errors:
        print(error)
    print(f"Checked {len(files)} publication files; {len(errors)} link issues")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
