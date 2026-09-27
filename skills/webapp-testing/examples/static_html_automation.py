"""Inspect local HTML using a portable file URI, including paths with spaces."""
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--html", type=Path, required=True)
    parser.add_argument("--ready-selector", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if not args.html.is_file():
        parser.error("--html must be an existing file")
    from playwright.sync_api import expect, sync_playwright

    args.output_dir.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.goto(args.html.resolve().as_uri())
            expect(page.locator(args.ready_selector)).to_be_visible()
            page.screenshot(path=str(args.output_dir / "static-page.png"), full_page=True)
        finally:
            browser.close()


if __name__ == "__main__":
    main()
