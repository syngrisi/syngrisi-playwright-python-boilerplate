"""Syngrisi visual-testing configuration.

Mirrors the JS boilerplate's ``syngrisi.config.ts``: it carries the server
``base_url``, an ``api_key`` (empty by default = auth off), the ``project``
name, the ``branch``, and an auto-generated ``run_name``/``run_ident``.

All values can be overridden via environment variables:

- ``SYNGRISI_URL``
- ``SYNGRISI_API_KEY``
- ``SYNGRISI_PROJECT``
- ``SYNGRISI_BRANCH``
- ``SYNGRISI_RUN_NAME``
- ``SYNGRISI_RUN_IDENT``
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
    "branch": os.environ.get("SYNGRISI_BRANCH", "main"),
    # If the env vars are not set, the values are generated automatically.
    "run_name": os.environ.get("SYNGRISI_RUN_NAME") or _generate_run_name(),
    "run_ident": os.environ.get("SYNGRISI_RUN_IDENT") or _generate_run_ident(),
}
