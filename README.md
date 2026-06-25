# Syngrisi Playwright Python Boilerplate

This boilerplate provides a starting point for writing automated UI tests with visual
regression capabilities, using **Playwright for Python** + **pytest** integrated with the
[Syngrisi](https://syngrisi.github.io/syngrisi/) Visual Testing Platform.

It is the Python counterpart of the
[JS Playwright boilerplate](https://github.com/syngrisi/syngrisi-playwright-boilerplate).
Instead of a high-level SDK it uses the low-level **Syngrisi core-api client**
(`syngrisi_core_api`) directly and wires the session/check glue itself. That client (a port
of the JS `@syngrisi/core-api`) is **bundled** in `syngrisi_core_api/` so the project runs
standalone; when a published package is available you can delete that folder and depend on
it instead.

## Requirements

- **Python >= 3.10**.
- A **Syngrisi server** running locally (default `http://localhost:3000/`), backed by
  **MongoDB >= 8** (default URI `mongodb://127.0.0.1:27017/SyngrisiDb`).
- Chromium for Playwright (installed in the steps below).

## Installation

```shell
git clone git@github.com:syngrisi/syngrisi-playwright-python-boilerplate.git
cd syngrisi-playwright-python-boilerplate
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m playwright install chromium
```

## Quick Start

### 1. Start the Syngrisi server

Start a Syngrisi server with authentication disabled (so the empty `api_key` works out of
the box). The quickest way is via the npm package (run it in a separate terminal):

```shell
SYNGRISI_AUTH=false npx -y @syngrisi/syngrisi@latest
```

It listens on [http://localhost:3000](http://localhost:3000) and needs MongoDB running. See
the [Syngrisi docs](https://syngrisi.github.io/syngrisi/) for other ways to run it (Docker,
etc.). For a real deployment, enable authentication and set the API key (see
[Configuration](#configuration--syngrisi_configpy)).

### 2. Run the tests

```shell
.venv/bin/pytest -q
```

Run a single file / browser:

```shell
.venv/bin/pytest tests/test_basic_example.py
.venv/bin/pytest --browser chromium
```

On the **first run** there are no baselines yet, so every check returns status `new` and the
tests **pass** (each prints a warning + a check link).

### 3. Review snapshots

Open the Syngrisi web UI ([http://localhost:3000](http://localhost:3000)), review the new
snapshots and **accept** the ones that look correct. On subsequent runs the new screenshots
are compared against the accepted baselines: a match `passed`, a mismatch `failed`. Every
check prints a direct link: `http://localhost:3000/?checkId=<id>&modalIsOpen=true`.

## Test examples

- [`tests/test_basic_example.py`](./tests/test_basic_example.py) — basic visual checks for an
  **element** (`#graph`), the **viewport** and the **full page**.
- [`tests/test_extended_example.py`](./tests/test_extended_example.py) — a data-driven graph
  (`?version=0`; switch to `?version=1` to break it) and a full **About** page check.
- [`tests/test_responsive_example.py`](./tests/test_responsive_example.py) — the same page
  captured at **mobile / tablet / desktop** breakpoints (one check per breakpoint).

All examples target the demo app
[`https://viktor-silakov.github.io/syngrisi-demo-app/`](https://viktor-silakov.github.io/syngrisi-demo-app/)
and run in Chromium.

## How it works

### Session lifecycle — the `syngrisi` fixture

[`conftest.py`](./conftest.py) defines the `syngrisi` fixture (the analogue of the JS
`syngrisi.fixture.ts`):

1. Creates a `SyngrisiApi` client from `syngrisi_config.py`.
2. **Before each test** it calls `start_session(...)` with the test/suite metadata + config,
   capturing the returned `testId`.
3. **After each test** it calls `stop_session(...)`.

### Visual checks — `match_baseline`

`match_baseline(target, check_name, request=request, **options)` is the helper (the analogue
of the JS `toMatchBaseline` matcher):

```python
from conftest import match_baseline

def test_example(syngrisi, page, request):
    page.goto("https://viktor-silakov.github.io/syngrisi-demo-app/")
    match_baseline(page.locator("#graph"), "Main graph", request=request)
    match_baseline(page, "Main viewport", request=request)
    match_baseline(page, "Full page", request=request, full_page=True)
```

`match_baseline(target, check_name, ...)`:

1. takes a screenshot of the `Page` (viewport / full page) or `Locator` (element),
2. computes the SHA-512 hex hash of the image (matching the Syngrisi server-side `imghash`),
3. calls `core_check(image_bytes, params)` with all required fields (`name`, `viewport`,
   `browserName`, `os`, `app`, `branch`, `testId`, `suite`, `browserVersion`,
   `browserFullVersion`, `hashCode`),
4. handles the returned status:
   - `new` → **pass** + warning + check link (first run, no baseline yet),
   - `failed` → **assertion failure** with the check link + fail reasons,
   - `passed` (or anything else) → **pass**,
5. logs the check link `${base_url}?checkId=${_id}&modalIsOpen=true`.

> 💡 Add `syngrisi`, `page` and `request` to the test arguments — `syngrisi` activates the
> session and `request` lets `match_baseline` reach it.

### Configuration — `syngrisi_config.py`

[`syngrisi_config.py`](./syngrisi_config.py) holds the settings (the analogue of the JS
`syngrisi.config.ts`). Defaults:

| Setting     | Default                  | Env override         |
|-------------|--------------------------|----------------------|
| `base_url`  | `http://localhost:3000/` | `SYNGRISI_URL`       |
| `api_key`   | empty (auth off)         | `SYNGRISI_API_KEY`   |
| `project`   | `Boilerplate Python`     | `SYNGRISI_PROJECT`   |
| `branch`    | `main`                   | `SYNGRISI_BRANCH`    |
| `run_name`  | auto-generated           | `SYNGRISI_RUN_NAME`  |
| `run_ident` | auto-generated (UUID)    | `SYNGRISI_RUN_IDENT` |

## Bundled core-api client

The Syngrisi client is **bundled** in [`syngrisi_core_api/`](./syngrisi_core_api) (a port of
the JS `@syngrisi/core-api`). It is imported directly by the fixture, so the project runs
standalone — `requirements.txt` only needs `requests` for it. When a published package
becomes available, delete `syngrisi_core_api/` and add it as a normal dependency instead.

## CI

A GitHub Actions workflow is provided in
[`.github/workflows/tests.yml`](./.github/workflows/tests.yml): it spins up a MongoDB
service, installs deps + Chromium, starts the Syngrisi server (auth off), and runs the tests.

## License

MIT.
