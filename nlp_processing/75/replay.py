import argparse
import os
import re
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

SANDBOX_URL = Path(__file__).with_name("sandbox.html").resolve().as_uri()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "ticket",
        nargs="?",
        default=os.environ.get("TICKET_ID", "DEMO-042"),
        help="Demo ticket ID, for example DEMO-042 (default: TICKET_ID or DEMO-042)",
    )
    parser.add_argument("--manual", action="store_true", help="Pause before submission")
    parser.add_argument("--shift-layout", action="store_true")
    args = parser.parse_args()
    if not re.fullmatch(r"DEMO-[0-9]{3}", args.ticket):
        parser.error("ticket must match DEMO-000 (three digits)")

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=not args.manual)
        page = browser.new_page(viewport={"width": 960, "height": 540})
        page.goto(SANDBOX_URL + ("?layout=shifted" if args.shift_layout else ""))
        page.get_by_label("Ticket ID").fill(args.ticket)
        if args.manual:
            print(
                "Submit the ticket in Chromium, then click Resume in Playwright Inspector.",
                flush=True,
            )
            page.pause()
        else:
            page.get_by_role("button", name="Submit").click()

        expected = f"Saved: {args.ticket}"
        expect(page.get_by_role("status")).to_have_text(expected)
        print(expected)
        browser.close()
