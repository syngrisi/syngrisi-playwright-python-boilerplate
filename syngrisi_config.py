"""Syngrisi visual-testing configuration.

Mirrors the JS boilerplate `syngrisi.config.ts`:

- ``base_url``  — URL of the Syngrisi server.
- ``api_key``   — API key for authentication (empty = auth off, the default).
- ``project``   — name of the project under test (the Syngrisi "app").
- ``branch``    — version-control branch name.
- ``run_name`` / ``run_ident`` — unique identifiers for the test run. If not
  provided via the ``SYNGRISI_RUN_NAME`` / ``SYNGRISI_RUN_IDENT`` env vars they
  are generated automatically (timestamp + uuid).
"""

import os
import uuid
from datetime import datetime


def _generate_run_name() -> str:
    return f"Run {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"


def _generate_run_ident() -> str:
    return str(uuid.uuid4())


config = {
    "base_url": os.environ.get("SYNGRISI_URL", "http://localhost:3000/"),
    "api_key": os.environ.get("SYNGRISI_API_KEY", ""),
    "project": os.environ.get("SYNGRISI_PROJECT", "Boilerplate Python"),
    "branch": "main",
    # If the env vars are not set, the values are generated automatically.
    "run_name": os.environ.get("SYNGRISI_RUN_NAME") or _generate_run_name(),
    "run_ident": os.environ.get("SYNGRISI_RUN_IDENT") or _generate_run_ident(),
}
