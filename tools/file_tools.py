"""Tool 3 — File creator. Writes to a shared folder (Manual 23.3).

Defaults to a local, writable path so it works on a laptop; the container path
``/srv/shared-files`` is used automatically when it exists.
"""

import os
from datetime import datetime
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _shared_root() -> str:
    env = os.environ.get("SHARED_FILES_DIR")
    if env:
        return env
    if os.path.isdir("/srv/shared-files") and os.access("/srv/shared-files", os.W_OK):
        return "/srv/shared-files"
    return str(_PROJECT_ROOT / "data" / "shared-files")


def create_file(filename: str, content: str, subfolder: str = "") -> dict:
    root = _shared_root()
    folder = os.path.join(root, subfolder) if subfolder else root
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, filename)
    with open(path, "w") as f:
        f.write(content)
    return {"path": path, "size": os.path.getsize(path), "created": datetime.now().isoformat()}
