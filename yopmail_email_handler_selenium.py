import uuid
import os
import re
import time

from bs4 import BeautifulSoup  # kept in case you want more parsing later
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


# ================================================================
# Basic config
# ================================================================
YOPMAIL_BASE_URL = "https://yopmail.com/"


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

    option = None    # type: ignore[assignment]
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
# Selenium helpers (Firefox)
# ================================================================
def create_driver() -> webdriver.Firefox:
    """
    Create a Firefox WebDriver instance with some sensible defaults.
    """
    options = FirefoxOptions()
    # If you want headless, uncomment the next line:
    # options.add_argument("-headless")

    driver = webdriver.Firefox(options=options)
    driver.set_window_size(1200, 800)
    return driver


def wait_for_iframe(driver, frame_name: str, timeout: int = 15):
    """
    Wait until an iframe with given name/id is available and switch into it.
    """
    WebDriverWait(driver, timeout).until(
        EC.frame_to_be_available_and_switch_to_it((By.NAME, frame_name))
    )


def get_inbox_message_elements(driver, mailbox_name: str):
    """
    Load YOPmail for the given mailbox and return the Selenium elements
    for each message row in the inbox iframe.

    Uses the HTML structure you pasted:
      <div class="m" id="e_...">
          ...
          <button class="lm" onclick="g(this);">...</button>
      </div>
    """
    url = f"{YOPMAIL_BASE_URL}?login={mailbox_name}"
    print(f"[INFO] Loading YOPMAIL: {url}")
    driver.get(url)

    # Wait for the inbox iframe to appear and switch into it
    try:
        wait_for_iframe(driver, "ifinbox", timeout=20)
    except TimeoutException:
        print("[ERROR] Inbox iframe 'ifinbox' not found.")
        return []

    # Now we are inside the inbox iframe context
    msgs = driver.find_elements(By.CSS_SELECTOR, "div.m[id^='e_']")
    print(f"[INFO] Found {len(msgs)} message(s) in inbox.")
    return msgs


def get_mail_html_for_message(driver, msg_element) -> str:
    """
    Given a message row element inside the inbox iframe, click it and
    return the HTML of the email body from the 'ifmail' iframe.
    """
    # We assume driver is currently inside ifinbox when this is called
    try:
        button = msg_element.find_element(By.CSS_SELECTOR, "button.lm")
        button.click()
    except Exception as e:
        print(f"[WARNING] Could not click message row: {e}")
        return ""

    # Switch back to top, then into the mail iframe
    driver.switch_to.default_content()

    try:
        wait_for_iframe(driver, "ifmail", timeout=20)
    except TimeoutException:
        print("[WARNING] Mail iframe 'ifmail' not found after clicking message.")
        return ""

    # Once inside ifmail, get the page source
    html = driver.page_source

    # Leave caller to handle going back into ifinbox if needed
    driver.switch_to.default_content()
    return html


# ================================================================
# Main logic: poll inbox & find JotForm link
# ================================================================
def try_to_get_jotform_link(email: str) -> None:
    mailbox_name = email.split("@")[0].strip().lower()
    print(f"\n[INFO] Using YOPmail mailbox: '{mailbox_name}'")

    driver = create_driver()

    max_attempts = 12
    poll_interval = 5  # seconds

    try:
        print(f"\n[INFO] Checking inbox with polling (max {max_attempts * poll_interval} seconds)...")

        msgs = []
        for attempt in range(1, max_attempts + 1):
            print(f"[ATTEMPT {attempt}/{max_attempts}] Fetching inbox messages...")
            msgs = get_inbox_message_elements(driver, mailbox_name)

            if msgs:
                break

            if attempt < max_attempts:
                print(f"[INFO] No emails yet, waiting {poll_interval} seconds...")
                time.sleep(poll_interval)

            # Ensure we’re back at the top before the next attempt
            driver.switch_to.default_content()

        if not msgs:
            print("\n[INFO] No emails found after polling. The email might not have arrived yet.")
            print(f"[TIP] Check manually at: https://yopmail.com/?login={mailbox_name}")
            return

        num_msgs = len(msgs)
        print(f"\n[INFO] Scanning {num_msgs} email(s) for JotForm link...\n")

        found_link = False

        # Iterate by index to avoid stale element issues,
        # re-entering the inbox iframe each time
        for idx in range(num_msgs):
            # Always start from top-level
            driver.switch_to.default_content()
            try:
                wait_for_iframe(driver, "ifinbox", timeout=10)
            except TimeoutException:
                print("[ERROR] Lost inbox iframe before reading messages.")
                break

            current_msgs = driver.find_elements(By.CSS_SELECTOR, "div.m[id^='e_']")
            if idx >= len(current_msgs):
                break

            msg = current_msgs[idx]
            mail_id = msg.get_attribute("id") or f"<no id idx={idx}>"
            print(f"[INFO] Reading message {idx+1}/{num_msgs} ({mail_id})...")

            html_body = get_mail_html_for_message(driver, msg)
            if not html_body:
                continue

            link = extract_jotform_link(html_body)
            if link:
                print(f"[FOUND JOTFORM LINK]: {link}")
                found_link = True
                break

        if not found_link:
            print("[INFO] No JotForm edit link found in inbox.")

    finally:
        driver.quit()


# ================================================================
# Entry point
# ================================================================
if __name__ == "__main__":
    email = ask_user_for_email()
    try_to_get_jotform_link(email)
