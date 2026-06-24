"""Tool 2 — Code execution sandbox (Manual 23.2).

Runs Python in a subprocess with a timeout. This is a real local tool (no API
cost), used by hermes-builder/research/finance for scaffolding and data work.
"""

import subprocess
import sys
import tempfile
import os


def run_python_code(code: str, timeout: int = 30) -> dict:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        tmp = f.name
    try:
        r = subprocess.run(
            [sys.executable, tmp], capture_output=True, text=True, timeout=timeout
        )
        return {"stdout": r.stdout, "stderr": r.stderr, "returncode": r.returncode}
    except subprocess.TimeoutExpired:
        return {"stdout": "", "stderr": "Timeout", "returncode": -1}
    finally:
        os.unlink(tmp)
