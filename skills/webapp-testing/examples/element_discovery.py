"""Discover elements after explicit readiness; all artifacts stay in --output-dir."""
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    parser.add_argument("--ready-selector", required=True)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    from playwright.sync_api import expect, sync_playwright

    args.output_dir.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.goto(args.url, wait_until="domcontentloaded")
            expect(page.locator(args.ready_selector)).to_be_visible()
            for label, selector in [("buttons", "button"), ("links", "a[href]"),
                                    ("inputs", "input, textarea, select")]:
                print(f"{label}: {page.locator(selector).count()}")
            page.screenshot(path=str(args.output_dir / "page-discovery.png"), full_page=True)
        finally:
            browser.close()


if __name__ == "__main__":
    main()
