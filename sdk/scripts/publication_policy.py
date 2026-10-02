"""Fail-closed content checks shared by the checker and clean ZIP exporter."""

import re

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
EXCLUDED_PARTS = {
    "__pycache__",
    "work",
    "build",
    "dist",
    ".git",
    ".venv",
    ".pytest_cache",
    ".ruff_cache",
}
TEXT_SUFFIXES = {
    ".md",
    ".py",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
    ".svg",
    ".json",
    ".html",
    ".css",
    ".js",
}
MAX_FILE_BYTES = 5 * 1024 * 1024
MAX_BUNDLE_BYTES = 50 * 1024 * 1024
PRIVATE_NAMES = {
    "validation.md",
    "cpu-training-live.md",
    "research_state.md",
    "custom-features-engineering.zh-cn.md",
}
# Compose signatures so their definitions do not match the scanner itself.
SENSITIVE = re.compile(
    r"(?:gh[pousr]_"
    + r"[A-Za-z0-9]{30,}|github_"
    + r"pat_[A-Za-z0-9_]{30,}"
    + r"|sk-"
    + r"[A-Za-z0-9]{32,}|dp_"
    + r"[A-Za-z0-9_-]{32,}"
    + r"|-----BEGIN "
    + r"(?:RSA |EC |OPENSSH )?PRIVATE KEY-----"
    + r"|/mnt/"
    + r"[a-z]/users/|[a-z]:"
    + r"\\users\\"
    + r"|\b192\.168\."
    + r"\d+\.\d+\b|\b10\."
    + r"\d+\.\d+\.\d+\b"
    + r"|\b172\.(?:1[6-9]|2\d|3[01])\."
    + r"\d+\.\d+\b"
    + r"|\bcn"
    + r"\d{2}\b|sg-d"
    + r"\d{2}-inner|/opt/"
    + r"datapanel[^\s]*"
    + r"|https?://[^/\s]+:[^/\s]+@)",
    re.IGNORECASE,
)
ASSIGNED_SECRET = re.compile(
    r"(?im)^[ \t]*(?:export[ \t]+)?(?:[A-Z_]*API_KEY|[A-Z_]*PASSWORD|[A-Z_]*SECRET|[A-Z_]*TOKEN)"
    r"[ \t]*=[ \t]*[\"']?([^\s\"'<>]+)"
)


def selected(relative):
    """Choose only the documented package surface; never include Git history."""
    return (
        not EXCLUDED_PARTS.intersection(relative.parts)
        and not any(part.endswith(".egg-info") for part in relative.parts)
        and (relative.parts[0] in ALLOWED_DIRS or str(relative) in ALLOWED_ROOT_FILES)
    )


def validate_content(relative, data):
    """Inspect exact bytes destined for publication, including JSON and HTML."""
    name = relative.name.lower()
    if name in PRIVATE_NAMES or name.startswith("retest-20"):
        raise ValueError(f"Internal report: {relative}")
    if (name.startswith(".env") and name != ".env.example") or name in {
        "credentials",
        "id_rsa",
        "id_ed25519",
    }:
        raise ValueError(f"Secret-bearing filename: {relative}")
    if relative.suffix.lower() not in TEXT_SUFFIXES and name not in {
        "license",
        ".gitignore",
        ".env.example",
    }:
        raise ValueError(f"Unreviewed file type: {relative}")
    if len(data) > MAX_FILE_BYTES or b"\x00" in data:
        raise ValueError(f"Oversized or binary file: {relative}")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        raise ValueError(f"Non-text file: {relative}") from None
    if SENSITIVE.search(text):
        # Report only a path; matched material might itself be a secret.
        raise ValueError(f"Potential private content: {relative}")
    for match in ASSIGNED_SECRET.finditer(text):
        value = match.group(1)
        if len(value) >= 16 and not any(
            marker in value.lower()
            for marker in (
                "replace",
                "example",
                "your_",
                "os.environ",
                "environ.get",
                "$",
                "getenv",
            )
        ):
            raise ValueError(f"Potential assigned credential: {relative}")
    return text


def collect(root):
    """Read once so checked bytes and exported bytes cannot diverge."""
    files, total = {}, 0
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if not selected(relative):
            continue
        if path.is_symlink():
            raise ValueError(f"Symlink in public package: {relative}")
        if not path.is_file():
            continue
        if path.stat().st_size > MAX_FILE_BYTES:
            raise ValueError(f"Oversized file: {relative}")
        data = path.read_bytes()
        validate_content(relative, data)
        total += len(data)
        if total > MAX_BUNDLE_BYTES:
            raise ValueError("Public package exceeds review size limit")
        files[relative] = data
    return files
