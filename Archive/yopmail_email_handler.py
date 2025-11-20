import uuid
import os
import re
import time
import requests
from bs4 import BeautifulSoup
from yopmail import Yopmail

# ================================================================
# Monkey-patch Yopmail.get_mail_ids to work with new YOPmail UI
# ================================================================
YOPMAIL_MAIN_URL = "https://yopmail.com/"
YOPMAIL_INBOX_URL = "https://yopmail.com/inbox"


def _patched_get_mail_ids(self, page: int = 1, proxies=None):
    """
    Replacement for Yopmail.get_mail_ids that:

      1. Loads the main YOPmail page with ?login=<username> to
         establish cookies/sessions.
      2. Calls /inbox?login=<username>&p=<page> with browser-like
         headers.
      3. Scrapes message IDs from the HTML using wm('ID') onclicks.

    This is as close as we can get to what the browser is doing,
    without running a real browser.
    """

    session = getattr(self, "session", requests.Session())

    # Spoof browser-y headers
    session.headers.setdefault(
        "User-Agent",
        (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
    )
    session.headers.setdefault("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
    session.headers.setdefault("Accept-Language", "en-GB,en;q=0.9")
    session.headers.setdefault("Connection", "keep-alive")

    if proxies is None and getattr(self, "proxies", None):
        proxies = self.proxies

    username = getattr(self, "username", "").split("@")[0]

    # Step 1: hit the main page to get cookies / session
    main_params = {"login": username}
    main_url = YOPMAIL_MAIN_URL
    try:
        resp_main = session.get(main_url, params=main_params, proxies=proxies)
        resp_main.raise_for_status()
    except requests.HTTPError as e:
        print(
            f"[ERROR] Initial YOPmail main-page request failed: {e}\n"
            f"       URL tried: {resp_main.url if 'resp_main' in locals() else main_url}\n"
        )
        return []

    # Step 2: call the inbox endpoint like the iframe does
    inbox_params = {
        "login": username,
        "p": page,
    }

    # Set a Referer header so we look like the iframe call
    session.headers["Referer"] = resp_main.url

    try:
        resp_inbox = session.get(YOPMAIL_INBOX_URL, params=inbox_params, proxies=proxies)
        resp_inbox.raise_for_status()
    except requests.HTTPError as e:
        body_preview = ""
        try:
            body_preview = resp_inbox.text[:200]
        except Exception:
            body_preview = "<no body>"
        print(
            f"[ERROR] Inbox request failed: {e}\n"
            f"       URL tried: {resp_inbox.url if 'resp_inbox' in locals() else YOPMAIL_INBOX_URL}\n"
            f"       Status: {resp_inbox.status_code if 'resp_inbox' in locals() else 'unknown'}\n"
            f"       Body (first 200 chars): {body_preview!r}"
        )
        return []

    html = resp_inbox.text

    if "Complete the CAPTCHA to continue" in html:
        print("[WARN] YOPmail is showing a CAPTCHA. Automation is blocked.")
        return []

    soup = BeautifulSoup(html, "html.parser")
    mail_ids = []

    # ------------------------------------------------------------
    # SELECTOR SECTION:
    #
    # We expect something like:
    #   <tr class="m" onclick="wm('e_ZwAbCdEf123')">...</tr>
    #
    # This captures all IDs passed into wm('...').
    # ------------------------------------------------------------
    for tag in soup.find_all(attrs={"onclick": True}):
        onclick = tag.get("onclick", "")
        m = re.search(r"wm\('([^']+)'\)", onclick)
        if m:
            mail_ids.append(m.group(1))

    # Debug if needed:
    # if not mail_ids:
    #     print("DEBUG inbox HTML (first 2000 chars):")
    #     print(html[:2000])

    return mail_ids


# Apply the monkey-patch
Yopmail.get_mail_ids = _patched_get_mail_ids


# ================================================================
# Save & Load Email from File
# ================================================================
def save_email(email: str, filename: str = "yopmail_address.txt") -> None:
    with open(filename, "w") as f:
        f.write(email)
    print(f"[INFO] Saved generated email to {filename} (reference only)")


def load_email(filename: str = "yopmail_address.txt") -> str | None:
    if not os.path.exists(filename):
        print(f"[INFO] No saved YOPmail address found in {filename}.")
        return None
    with open(filename, "r") as f:
        email = f.read().strip()
    if email:
        print(f"[INFO] Loaded saved YOPmail address from {filename}: {email}")
        return email
    print(f"[INFO] {filename} is empty.")
    return None


# ================================================================
# Email Generation / Selection
# ================================================================
def create_random_email() -> str:
    mailbox = uuid.uuid4().hex
    return f"{mailbox}@yopmail.com"


def ask_user_for_email() -> str:
    print("----- YOPMAIL EMAIL HANDLER -----\n")
    print("1 = Create new unguessable YOPmail")
    print("2 = Use your own email (or load saved one)\n")

    option = None
    while option not in {"1", "2"}:
        option = input("Enter option 1 or 2: ").strip()

    if option == "1":
        email = create_random_email()
        print(f"[NEW YOPMAIL]: {email}")
        save_email(email)
        return email

    email = input(
        "Enter a YOPmail address (or press ENTER to load saved one): "
    ).strip()

    if not email:
        saved = load_email()
        if not saved:
            saved = create_random_email()
            save_email(saved)
        email = saved

    print(f"[USING EMAIL]: {email}")
    return email


# ================================================================
# Extract JotForm edit link from email HTML
# ================================================================
def extract_jotform_link(html: str) -> str | None:
    """
    Find an EEL JotForm *edit* link in the given HTML.

    Example:
      https://eel.jotform.com/edit/6392716199412043114?eapeo1e

    Rules:
      - always /edit/
      - digits segment dynamic
      - suffix either eapeo1e or eapet2e
    """
    pattern = r"(https://eel\.jotform\.com/edit/\d+\?(?:eapeo1e|eapet2e))"
    match = re.search(pattern, html)
    return match.group(1) if match else None


# ================================================================
# Main polling / retrieval logic
# ================================================================
def try_to_get_jotform_link(email: str) -> None:
    mailbox_name = email.split("@")[0].strip().lower()
    print(f"\n[INFO] Instantiating Yopmail for mailbox: '{mailbox_name}'")

    yp = Yopmail(mailbox_name, proxies=None)

    max_attempts = 12
    poll_interval = 5  # seconds

    print(f"\n[INFO] Checking inbox with polling (max {max_attempts * poll_interval} seconds)...")

    mail_ids: list[str] = []

    for attempt in range(1, max_attempts + 1):
        print(f"[ATTEMPT {attempt}/{max_attempts}] Fetching emails...")

        current_ids: list[str] = []

        for page in range(1, 6):
            try:
                ids = yp.get_mail_ids(page=page)
                if ids:
                    current_ids.extend(ids)
            except Exception as e:
                print(f"[WARNING] Error fetching mail IDs on page {page}: {e}")
                if page == 1:
                    break
                continue

        if current_ids:
            mail_ids = current_ids
            break

        if attempt < max_attempts:
            print(f"[INFO] No emails yet, waiting {poll_interval} seconds...")
            time.sleep(poll_interval)

    if not mail_ids:
        print("\n[INFO] No emails found after polling. The email might not have arrived yet.")
        print(f"[TIP] Check manually at: https://yopmail.com/?login={mailbox_name}")
        return

    print(f"\n[INFO] Scanning {len(mail_ids)} email(s) for JotForm link...\n")

    found_link = False

    for mail_id in mail_ids:
        try:
            mail = yp.get_mail_body(mail_id, show_image=True)
            html_body = getattr(mail, "body", "") or str(mail)

            link = extract_jotform_link(html_body)
            if link:
                print(f"[FOUND JOTFORM LINK]: {link}")
                found_link = True
                break
        except Exception as e:
            print(f"[WARNING] Error reading mail {mail_id}: {e}")
            continue

    if not found_link:
        print("[INFO] No JotForm edit link found in inbox.")


# ================================================================
# Entry point
# ================================================================
if __name__ == "__main__":
    email = ask_user_for_email()
    try_to_get_jotform_link(email)
