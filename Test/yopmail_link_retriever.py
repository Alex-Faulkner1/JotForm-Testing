"""
YOPmail Link Retriever - Finds JotForm approval links by EFS Reference
Integrated with test automation for automatic approval link retrieval
"""
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


YOPMAIL_BASE_URL = "https://yopmail.com/"

# Approver email addresses
APPROVER_EMAILS = {
    "PCM": "5497b0691aac47498821b0a603017505@yopmail.com",
    # Add more approvers later:
    # "RD": "another_address@yopmail.com",
    # "RCM": "yet_another@yopmail.com",
}


class YOPmailLinkRetriever:
    """Retrieve JotForm approval links from YOPmail inbox by EFS Reference."""
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.driver = None
    
    def _create_driver(self) -> webdriver.Firefox:
        """Create a Firefox WebDriver instance."""
        options = FirefoxOptions()
        if self.headless:
            options.add_argument("-headless")
        
        driver = webdriver.Firefox(options=options)
        driver.set_window_size(1200, 800)
        return driver
    
    def _wait_for_iframe(self, frame_name: str, timeout: int = 15):
        """Wait until an iframe is available and switch into it."""
        WebDriverWait(self.driver, timeout).until(
            EC.frame_to_be_available_and_switch_to_it((By.NAME, frame_name))
        )
    
    def _extract_jotform_link(self, html: str) -> str | None:
        """
        Find an EEL JotForm edit link in the given HTML.
        Pattern: https://eel.jotform.com/edit/DIGITS?eapeo1e or eapet2e
        """
        pattern = r"(https://eel\.jotform\.com/edit/\d+\?(?:eapeo1e|eapet2e))"
        match = re.search(pattern, html)
        return match.group(1) if match else None
    
    def _extract_efs_ref(self, html: str) -> str | None:
        """
        Extract EFS Reference from email HTML.
        Looking for patterns like: DEV_PR395, EFS-123456, etc.
        """
        # Try multiple patterns - now supports alphanumeric references
        patterns = [
            # Alphanumeric with underscores (e.g., DEV_PR395, TEST_123)
            r"EFS Ref:?\s*([A-Z0-9_]+)",
            # Standard numeric formats
            r"EFS[- ]?(\d{6})",
            r"Reference:?\s*EFS[- ]?(\d{6})",
        ]

        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                # Return the captured reference as-is
                ref = match.group(1)
                # If it's purely numeric, add EFS- prefix for consistency
                if ref.isdigit():
                    return f"EFS-{ref}"
                # Otherwise return as-is (e.g., DEV_PR395)
                return ref

        return None

    def _get_inbox_messages(self, mailbox_name: str) -> list:
        """Load YOPmail inbox and return message elements."""
        url = f"{YOPMAIL_BASE_URL}?login={mailbox_name}"
        print(f"    📬 Loading YOPmail inbox: {mailbox_name}")
        self.driver.get(url)

        try:
            self._wait_for_iframe("ifinbox", timeout=20)
        except TimeoutException:
            print("    ❌ Inbox iframe not found")
            return []

        msgs = self.driver.find_elements(By.CSS_SELECTOR, "div.m[id^='e_']")
        print(f"    📧 Found {len(msgs)} message(s)")
        return msgs

    def _get_email_content(self, msg_element) -> str:
        """Click a message and return its HTML content."""
        try:
            button = msg_element.find_element(By.CSS_SELECTOR, "button.lm")
            button.click()
        except Exception as e:
            print(f"    ⚠️  Could not click message: {e}")
            return ""

        # Switch to mail iframe
        self.driver.switch_to.default_content()

        try:
            self._wait_for_iframe("ifmail", timeout=20)
        except TimeoutException:
            print("    ⚠️  Mail iframe not found")
            return ""

        html = self.driver.page_source
        self.driver.switch_to.default_content()
        return html

    def get_approval_link(self, approver_stage: str, efs_ref: str,
                         max_attempts: int = 24, poll_interval: int = 5) -> str | None:
        """
        Get approval link for a specific EFS Reference from YOPmail.

        Args:
            approver_stage: Approver stage (e.g., "PCM", "RD", "RCM")
            efs_ref: EFS Reference number (e.g., "DEV_PR395", "EFS-123456")
            max_attempts: Maximum polling attempts (default 24 = 2 minutes)
            poll_interval: Seconds between polling attempts (default 5)

        Returns:
            JotForm edit link if found, None otherwise
        """
        email = APPROVER_EMAILS.get(approver_stage)
        if not email:
            print(f"    ❌ No email configured for approver stage: {approver_stage}")
            return None

        mailbox_name = email.split("@")[0].strip().lower()

        print(f"\n    🔍 Searching for approval link...")
        print(f"    📧 Approver: {approver_stage}")
        print(f"    🔖 EFS Ref: {efs_ref}")
        print(f"    ⏱️  Max wait: {max_attempts * poll_interval} seconds")

        self.driver = self._create_driver()

        try:
            for attempt in range(1, max_attempts + 1):
                print(f"\n    [Attempt {attempt}/{max_attempts}]")

                # Get inbox messages
                msgs = self._get_inbox_messages(mailbox_name)

                if not msgs:
                    if attempt < max_attempts:
                        print(f"    ⏳ No emails yet, waiting {poll_interval}s...")
                        time.sleep(poll_interval)
                    continue

                # Search through messages for matching EFS Ref
                print(f"    🔎 Scanning {len(msgs)} email(s)...")

                for idx in range(len(msgs)):
                    # Re-enter inbox iframe
                    self.driver.switch_to.default_content()
                    try:
                        self._wait_for_iframe("ifinbox", timeout=10)
                    except TimeoutException:
                        print("    ❌ Lost inbox iframe")
                        break

                    # Re-fetch messages (avoid stale elements)
                    current_msgs = self.driver.find_elements(By.CSS_SELECTOR, "div.m[id^='e_']")
                    if idx >= len(current_msgs):
                        break

                    msg = current_msgs[idx]
                    html_content = self._get_email_content(msg)

                    if not html_content:
                        continue

                    # Check if this email contains the target EFS Ref
                    email_efs = self._extract_efs_ref(html_content)
                    print(f"       Email {idx+1}: Found EFS Ref = {email_efs}")

                    # Case-insensitive comparison
                    if email_efs and email_efs.upper() == efs_ref.upper():
                        print(f"    ✅ Found email with {efs_ref}")

                        # Extract JotForm link
                        link = self._extract_jotform_link(html_content)

                        if link:
                            print(f"    🎯 Approval link found!")
                            return link
                        else:
                            print(f"    ⚠️  Email contains {efs_ref} but no JotForm link")

                # If we've checked all current emails and found nothing, wait and try again
                if attempt < max_attempts:
                    print(f"    ⏳ No match found, waiting {poll_interval}s...")
                    time.sleep(poll_interval)

            print(f"\n    ❌ No approval link found after {max_attempts} attempts")
            print(f"    💡 Check manually at: https://yopmail.com/?login={mailbox_name}")
            return None

        finally:
            self.driver.quit()


def get_approval_link_for_test(approver_stage: str, efs_ref: str) -> str | None:
    """
    Convenience function for getting approval links during test execution.

    Args:
        approver_stage: Approver stage (e.g., "PCM", "RD")
        efs_ref: EFS Reference number (e.g., "EFS-123456")

    Returns:
        JotForm approval link or None
    """
    retriever = YOPmailLinkRetriever(headless=True)
    return retriever.get_approval_link(approver_stage, efs_ref)


# Test function
if __name__ == "__main__":
    print("\n" + "="*60)
    print("YOPmail Link Retriever - Test Mode")
    print("="*60)

    # Example usage
    test_efs_ref = input("\nEnter EFS Reference to search for (e.g., DEV_PR395 or EFS-123456): ").strip()
    approver = input("Enter approver stage (PCM/RD/RCM): ").strip().upper()

    if test_efs_ref and approver:
        link = get_approval_link_for_test(approver, test_efs_ref)

        if link:
            print(f"\n✅ SUCCESS!")
            print(f"Link: {link}")
        else:
            print(f"\n❌ No link found")
    else:
        print("❌ Invalid input")