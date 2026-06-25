"""Extended visual-testing example: broken-data graph and an About full page.

Tests target different versions of the demo app via the ``?version=`` query
parameter to simulate visual changes. The commented lines show how to "break"
a check so you can see a ``failed`` status in Syngrisi.
"""

from conftest import match_baseline

DEMO_URL = "https://viktor-silakov.github.io/syngrisi-demo-app/"


def test_graph_broken_data(syngrisi, page, request):
    page.goto(f"{DEMO_URL}?version=0")
    # 💡 Broken version of the app — swap the line above for the one below to
    # break the graph check:
    # page.goto(f"{DEMO_URL}?version=1")

    page.locator("#graph").wait_for()
    match_baseline(page.locator("#graph"), "Sales Chart", request=request)


def test_about_full_page(syngrisi, page, request):
    page.goto(f"{DEMO_URL}?version=0")

    page.get_by_role("link", name="About", exact=True).click()
    # 💡 Broken version — swap for the "About (Bug)" link to break the check:
    # page.get_by_role("link", name="About (Bug)", exact=True).click()

    page.get_by_role("heading", name="Lorem ipsum").wait_for()

    match_baseline(page, "About - full page", request=request, full_page=True)
