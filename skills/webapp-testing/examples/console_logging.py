"""Capture local console logs for an explicit link-to-result browser flow."""
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    parser.add_argument("--ready-selector", required=True)
    parser.add_argument("--link-name", required=True)
    parser.add_argument("--result-selector", required=True)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    from playwright.sync_api import expect, sync_playwright

    args.output_dir.mkdir(parents=True, exist_ok=True)
    messages = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.on("console", lambda message: messages.append(f"[{message.type}] {message.text}"))
            page.goto(args.url, wait_until="domcontentloaded")
            expect(page.locator(args.ready_selector)).to_be_visible()
            page.get_by_role("link", name=args.link_name, exact=True).click()
            expect(page.locator(args.result_selector)).to_be_visible()
        finally:
            browser.close()
            # Logs may contain private data; inspect/redact before sharing.
            (args.output_dir / "console.log").write_text("\n".join(messages), encoding="utf-8")
    print(f"Captured {len(messages)} console messages to the selected local folder.")


if __name__ == "__main__":
    main()
