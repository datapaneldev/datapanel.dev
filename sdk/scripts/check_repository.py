"""Check local documentation links and obvious public-package contamination."""

import re
from pathlib import Path
from urllib.parse import unquote


def main():
    root = Path(__file__).resolve().parents[1]
    ignored = {
        ".git",
        ".venv",
        "work",
        "build",
        "dist",
        "__pycache__",
        ".pytest_cache",
        ".ruff_cache",
    }
    errors, checked = [], 0
    private_names = {
        "validation.md",
        "cpu-training-live.md",
        "RESEARCH_STATE.md",
        "custom-features-engineering.zh-CN.md",
    }
    for path in root.rglob("*"):
        if ignored.intersection(path.relative_to(root).parts):
            continue
        if path.name in private_names or path.name.startswith("retest-20"):
            errors.append(f"Internal report in public tree: {path.relative_to(root)}")
    # Construct patterns to avoid this checker matching its own literal definitions.
    private_prefix = "/mnt/" + "c/Users/"
    credential = re.compile(
        r"(?:gh[pousr]_" + r"[A-Za-z0-9]{30,}|sk-" + r"[A-Za-z0-9]{32,}|dp_" + r"[A-Za-z0-9_-]{48})"
    )
    for path in root.rglob("*"):
        if (
            not path.is_file()
            or ignored.intersection(path.relative_to(root).parts)
            or ".egg-info" in str(path)
        ):
            continue
        if path.suffix not in {".md", ".py", ".toml", ".txt", ".yaml", ".yml", ".svg"}:
            continue
        checked += 1
        text = path.read_text(encoding="utf-8")
        if private_prefix in text or credential.search(text):
            errors.append(f"Potential private content: {path.relative_to(root)}")
        if path.suffix == ".md":
            for target in re.findall(r"\]\(([^)]+)\)", text):
                if "://" in target or target.startswith("#"):
                    continue
                target = unquote(target.split("#")[0])
                if not (path.parent / target).exists():
                    errors.append(f"Broken link: {path.relative_to(root)} -> {target}")
    for error in errors:
        print(error)
    print(f"Checked {checked} source/document files; {len(errors)} issues")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
