"""Basic visual-testing example: element, viewport and full page.

Note: you must depend on the ``syngrisi`` fixture (and ``page``) to activate the
visual session, and pass ``request`` to ``match_baseline`` so it can reach the
session.
"""

from conftest import match_baseline

DEMO_URL = "https://viktor-silakov.github.io/syngrisi-demo-app/"


def test_simple_viewport_and_element(syngrisi, page, request):
    page.goto(DEMO_URL)
    page.locator("#graph").wait_for()

    match_baseline(page.locator("#graph"), "Main graph", request=request)
    match_baseline(page, "Main viewport", request=request)
    match_baseline(page, "Full page", request=request, full_page=True)
