"""EdVisingU agent tools (Manual Section 23).

Every tool defaults to a $0 mock and only touches a real third-party SDK when
``ARCH_BACKEND=live`` *and* the relevant API key is present. SDK imports are
lazy so the tools import cleanly even when those packages aren't installed.
"""

import os


def is_live(key_env: str | None = None) -> bool:
    """True only when live mode is on and (optionally) the key is present."""
    if os.environ.get("ARCH_BACKEND", "mock").strip().lower() != "live":
        return False
    if key_env and not os.environ.get(key_env):
        return False
    return True
