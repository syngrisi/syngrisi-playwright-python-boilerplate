"""Responsive visual-testing example.

Captures the same page at several viewport sizes. Each breakpoint produces a
separate Syngrisi check, so you get an independent baseline per breakpoint.
"""

import pytest

from conftest import match_baseline

DEMO_URL = "https://viktor-silakov.github.io/syngrisi-demo-app/"

BREAKPOINTS = [
    ("mobile", 375, 667),
    ("tablet", 768, 1024),
    ("desktop", 1280, 720),
]


@pytest.mark.parametrize("name,width,height", BREAKPOINTS)
def test_responsive(syngrisi, page, request, name, width, height):
    page.set_viewport_size({"width": width, "height": height})
    page.goto(f"{DEMO_URL}?version=0")
    page.locator("#graph").wait_for()

    match_baseline(page, f"Demo app - {name}", request=request)
