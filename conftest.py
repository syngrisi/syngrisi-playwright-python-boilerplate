"""Pytest fixtures and the ``match_baseline`` helper for Syngrisi visual checks.

This is the Python analogue of the JS boilerplate's ``syngrisi.fixture.ts``:

- a ``syngrisi`` session fixture that starts a Syngrisi test session before each
  test (using the test's metadata + config) and stops it afterwards;
- a ``match_baseline(page_or_locator, check_name, **screenshot_opts)`` helper
  that screenshots the page/element, sends it to Syngrisi as a check, and
  asserts on the returned status (``new`` -> pass + warning, ``failed`` ->
  assertion failure, ``passed`` -> pass).

The helper is intentionally simple and reliable: it does not implement the JS
hash-wait-for-baseline loop or diff-image attachment, but it does the full
new/failed/passed handling and always prints the check link.
"""

import hashlib
import platform

import pytest
from playwright.sync_api import Locator, Page
from syngrisi_core_api import SyngrisiApi, transform_os

from syngrisi_config import config


def _image_hash(image_bytes: bytes) -> str:
    """SHA-512 hex digest of the image (matches the server's ``imghash``)."""
    return hashlib.sha512(image_bytes).hexdigest()


def _get_os() -> str:
    """Normalized OS name, mirroring the JS ``getOS`` helper."""
    return transform_os(platform.system())


def _viewport_str(page: Page) -> str:
    size = page.viewport_size or {"width": 0, "height": 0}
    return f"{size['width']}x{size['height']}"


def _browser_versions(page: Page):
    """Return ``(short_version, full_version)`` for the active browser."""
    browser = page.context.browser
    full_version = browser.version if browser else "0.0.0.0"
    short_version = full_version.split(".")[0]
    return short_version, full_version


@pytest.fixture
def syngrisi(page: Page, request: pytest.FixtureRequest):
    """Start a Syngrisi session before the test and stop it after.

    Yields a ``(api, session)`` tuple, but tests normally only need to depend on
    the fixture to activate the session and then call ``match_baseline(...)``.
    """
    api = SyngrisiApi({"url": config["base_url"], "apiKey": config["api_key"]})

    test_name = request.node.name
    # Suite title: the test's module / class, mirroring the JS suite title.
    suite_name = request.node.parent.name if request.node.parent else test_name

    short_version, full_version = _browser_versions(page)

    session = api.start_session({
        "run": config["run_name"],
        "runident": config["run_ident"],
        "name": test_name,
        "suite": suite_name,
        "viewport": _viewport_str(page),
        "browser": page.context.browser.browser_type.name if page.context.browser else "chromium",
        "browserVersion": short_version,
        "browserFullVersion": full_version,
        "os": _get_os(),
        "app": config["project"],
        "branch": config["branch"],
    })

    if isinstance(session, dict) and session.get("error"):
        raise RuntimeError(f"Failed to start Syngrisi session: {session}")

    test_id = session.get("_id") or session.get("id")
    if not test_id:
        raise RuntimeError(f"Syngrisi session has no test id: {session}")

    # Stash everything the helper needs on the test node.
    request.node._syngrisi = {
        "api": api,
        "test_id": test_id,
        "suite": suite_name,
        "page": page,
    }

    yield api, session

    api.stop_session(test_id)


def _check_link(check_id: str) -> str:
    return f"{config['base_url']}?checkId={check_id}&modalIsOpen=true"


def match_baseline(page_or_locator, check_name: str, request: pytest.FixtureRequest = None, **screenshot_opts):
    """Take a screenshot and run a Syngrisi visual check.

    :param page_or_locator: a Playwright ``Page`` or ``Locator``.
    :param check_name: the Syngrisi check name.
    :param request: the pytest ``request`` fixture (needed to reach the session).
    :param screenshot_opts: passed straight to Playwright's ``screenshot``
        (e.g. ``full_page=True``).

    Status handling (raises ``AssertionError`` on ``failed``):
      - ``new``    -> pass, but log a warning + the check link.
      - ``failed`` -> assertion failure with the check link + reasons.
      - ``passed`` -> pass.
    """
    if request is None:
        raise ValueError("match_baseline requires the pytest `request` fixture")

    ctx = getattr(request.node, "_syngrisi", None)
    if ctx is None:
        raise RuntimeError(
            "Syngrisi session not started — add `syngrisi` to the test arguments"
        )

    api: SyngrisiApi = ctx["api"]
    page: Page = ctx["page"]

    # Wait for the page to settle before capturing. `networkidle` + a short
    # fixed delay lets load animations (e.g. the demo app's chart) finish, which
    # keeps deterministic screenshots stable across runs. This is the simple,
    # reliable alternative to the JS boilerplate's hash-wait-for-baseline loop.
    page.wait_for_load_state("load")
    try:
        page.wait_for_load_state("networkidle", timeout=5000)
    except Exception:
        pass
    page.wait_for_timeout(1000)

    image_bytes = page_or_locator.screenshot(**screenshot_opts)

    short_version, full_version = _browser_versions(page)

    result = api.core_check(image_bytes, {
        "name": check_name,
        "viewport": _viewport_str(page),
        "browserName": page.context.browser.browser_type.name if page.context.browser else "chromium",
        "os": _get_os(),
        "app": config["project"],
        "branch": config["branch"],
        "testId": ctx["test_id"],
        "suite": ctx["suite"],
        "browserVersion": short_version,
        "browserFullVersion": full_version,
        "hashCode": _image_hash(image_bytes),
    })

    if isinstance(result, dict) and result.get("error"):
        raise AssertionError(f"❌ Check '{check_name}' API error: {result}")

    # Status may be a string or a list that includes 'new'/'passed'/'failed'.
    status = result.get("status")
    statuses = status if isinstance(status, list) else [status]
    check_id = result.get("_id")
    link = f"🔗 {_check_link(check_id)}"

    if "new" in statuses:
        print(
            f"⚠️  Check '{check_name}' has a 'new' status — review and accept it "
            f"in Syngrisi, then re-run.\n{link}"
        )
        return result

    if "failed" in statuses:
        reasons = result.get("failReasons")
        raise AssertionError(
            f"❌ Check '{check_name}' failed to compare snapshots.\n"
            f"reasons: {reasons}\n{link}"
        )

    # passed (or any other non-failing status).
    print(f"✅ Check '{check_name}' passed.\n{link}")
    return result
