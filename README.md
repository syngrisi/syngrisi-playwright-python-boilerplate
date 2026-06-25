# Syngrisi Playwright (Python) Boilerplate

A starting point for visual regression testing with **Playwright for Python +
pytest**, integrated with the [Syngrisi](https://github.com/syngrisi/syngrisi)
visual-testing server via the local `syngrisi-core-api` Python client.

This is the Python analogue of the JS `@syngrisi/playwright-sdk` boilerplate: a
session fixture starts/stops a Syngrisi test session around each test, and a
`match_baseline(...)` helper screenshots the page/element and runs a visual
check.

## Requirements

- Python >= 3.10
- A running **Syngrisi server** (default `http://localhost:3000/`). It needs
  MongoDB >= 8 (default URI `mongodb://127.0.0.1:27017/SyngrisiDb`).

## Installation

```shell
git clone git@github.com:syngrisi/syngrisi-playwright-python-boilerplate.git
cd syngrisi-playwright-python-boilerplate
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m playwright install chromium
```

The Syngrisi client is bundled in `./syngrisi_core_api/` (a port of the JS
`@syngrisi/core-api`) so the project runs standalone — `requirements.txt` only
needs `requests` for it. When the Python core-api is published to PyPI you can
delete the bundled folder and depend on the package instead.

## Quick Start

### 1. Start the Syngrisi server

Start a Syngrisi server with authentication disabled so the empty `api_key`
works out of the box:

```shell
SYNGRISI_AUTH=false npx -y @syngrisi/syngrisi@latest start -d
```

For a real deployment, enable authentication and set `api_key` in
`syngrisi_config.py` to a key from your Syngrisi account settings.

### 2. Run the tests

```shell
.venv/bin/pytest -q
```

To run a single file / browser:

```shell
.venv/bin/pytest tests/test_basic_example.py
.venv/bin/pytest --browser chromium
```

On the **first run** there are no baselines, so every check returns status
`new` — the helper treats `new` as a **pass** (with a warning + the check link),
so a fresh run is fully green.

### 3. Review snapshots

Open the Syngrisi web interface (default
[http://localhost:3000](http://localhost:3000)), review the `new` checks and
accept them. On subsequent runs accepted checks compare against their baseline
and report `passed` or `failed`.

Every check prints a direct link:
`http://localhost:3000/?checkId=<id>&modalIsOpen=true`.

## Test examples

- [`tests/test_basic_example.py`](./tests/test_basic_example.py) — element
  (`#graph`), viewport and full-page checks.
- [`tests/test_extended_example.py`](./tests/test_extended_example.py) —
  broken-data graph (`?version=0`; comments show how to break it with
  `?version=1`) and an About full-page check.
- [`tests/test_responsive_example.py`](./tests/test_responsive_example.py) —
  the same page at mobile / tablet / desktop breakpoints (parametrized loop).

## How it works

The `syngrisi` fixture (in [`conftest.py`](./conftest.py)):

1. Creates a `SyngrisiApi` client from `syngrisi_config.py`.
2. Calls `start_session` with the test's metadata (name, suite) + config.
3. Yields, then calls `stop_session` after the test.

The `match_baseline(page_or_locator, check_name, request=request, **opts)`
helper:

1. Screenshots the page/element (`full_page=True` is supported via `**opts`).
2. Calls `core_check` with all required fields (name, viewport, browserName,
   os, app, branch, testId, suite, browserVersion, browserFullVersion, and a
   SHA-512 `hashCode` of the image).
3. Handles the returned status: `new` → pass + warning, `failed` → assertion
   failure with reasons, `passed` → pass. It always prints the check link.

```python
from conftest import match_baseline

def test_example(syngrisi, page, request):
    page.goto("https://viktor-silakov.github.io/syngrisi-demo-app/")
    match_baseline(page.locator("#graph"), "Main graph", request=request)
    match_baseline(page, "Full page", request=request, full_page=True)
```

> 💡 Add `syngrisi`, `page` and `request` to the test arguments — `syngrisi`
> activates the session and `request` lets `match_baseline` reach it.

## Configuration

`syngrisi_config.py` holds the settings:

- `base_url` — URL of the Syngrisi server (env: `SYNGRISI_URL`).
- `api_key` — API key (empty = auth off; env: `SYNGRISI_API_KEY`).
- `project` — project name (the Syngrisi "app"); here `"Boilerplate Python"`.
- `branch` — branch name.
- `run_name` / `run_ident` — auto-generated (timestamp / uuid) unless set via
  `SYNGRISI_RUN_NAME` / `SYNGRISI_RUN_IDENT`.

## CI

A GitHub Actions workflow is provided in
[`.github/workflows/tests.yml`](./.github/workflows/tests.yml): it spins up
MongoDB, installs deps + Chromium, starts the Syngrisi server, and runs the
tests.

## License

MIT.
