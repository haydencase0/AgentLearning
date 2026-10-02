from fnmatch import fnmatch
from pathlib import Path

# Files outside this directory can never be accessed by the agent.
SAFE_ROOT = Path(__file__).resolve().parent

# Names the agent may not read or see, matched against every path component.
SENSITIVE_PATTERNS = [".env", ".env.*"]


def _is_allowed(resolved: Path) -> bool:
    """Whether a resolved path is inside SAFE_ROOT and not sensitive."""
    if not resolved.is_relative_to(SAFE_ROOT):
        return False
    return not any(
        fnmatch(part, pattern)
        for part in resolved.relative_to(SAFE_ROOT).parts
        for pattern in SENSITIVE_PATTERNS
    )


def _resolve_safe(path: str) -> Path:
    # resolve() collapses ".." and follows symlinks, so the check below
    # sees the real location.
    target = (SAFE_ROOT / path).resolve()

    # Use one generic error for every case so we don't leak which paths exist.
    if not _is_allowed(target):
        raise PermissionError("Access denied or file not found.")

    return target


def read_safe_file(path: str) -> str:
    """Read a UTF-8 text file from the project directory.

    Args:
        path: File path relative to the project root, e.g. "docs/readme.txt".
    """
    target = _resolve_safe(path)
    if not target.is_file():
        raise PermissionError("Access denied or file not found.")

    return target.read_text(encoding="utf-8")

def read_personal_files() -> str:
    """Read text files from the designated personal_files/ folder.

    The tool intentionally takes no path argument. The agent can read only
    files inside personal_files/, not arbitrary files in the project.
    """
    personal_folder = _resolve_safe("personal_files")
    if not personal_folder.is_dir():
        raise PermissionError("Personal files folder not found.")

    supported_extensions = {".md", ".txt", ".json", ".yaml", ".yml", ".csv"}
    documents = []

    for target in sorted(personal_folder.rglob("*")):
        if not target.is_file() or target.suffix.lower() not in supported_extensions:
            continue
        if not _is_allowed(target.resolve()):
            continue

        relative_name = target.relative_to(personal_folder)
        contents = target.read_text(encoding="utf-8")
        documents.append(f"--- {relative_name} ---\n{contents}")

    return "\n\n".join(documents) or "(no personal files found)"


def list_directory(path: str = ".") -> str:
    """List the contents of a directory in the project. Subdirectories end with "/".

    Args:
        path: Directory path relative to the project root. Defaults to the root.
    """
    target = _resolve_safe(path)
    if not target.is_dir():
        raise PermissionError("Access denied or directory not found.")

    entries = sorted(
        entry.name + "/" if entry.is_dir() else entry.name
        for entry in target.iterdir()
        if _is_allowed(entry.resolve())
    )
    return "\n".join(entries) or "(empty directory)"
