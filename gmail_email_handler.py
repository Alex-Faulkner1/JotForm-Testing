"""
Gmail Approval Link Handler
---------------------------

Utility functions for retrieving JotForm approval links straight from
Gmail.  This replaces the previous YOPmail-based flow so the test runner
can automatically pick up approval links that are delivered to a real
Gmail inbox.
"""

from __future__ import annotations

import imaplib
import email
import re
import time
from email.message import Message
from typing import List, Optional

# =========================
# CONFIGURATION
# =========================
IMAP_SERVER = "imap.gmail.com"
IMAP_FOLDER = "INBOX"

EMAIL_ADDRESS = "mustapha.jobe0001@gmail.com"
APP_PASSWORD = "nuho iurm uepl klem"

SEARCH_SENDER = "noreply@formresponse.com"
POLL_INTERVAL_SECONDS = 5
DEFAULT_TIMEOUT_SECONDS = 180

# Hints to map approval stages to the unique approval code appended to the edit link
STAGE_LINK_HINTS = {
    "PCM": ["eapeo1e", "eapeo2e"],
    "RCM": ["eapeo1e", "eapeo2e"],
    "RD": ["eapet2e"],
}

LINK_PATTERN = re.compile(r"https://eel\.jotform\.com/edit/\d+\?[A-Za-z0-9=&_\-]+")


def _extract_html_body(msg: Message) -> Optional[str]:
    """Return the HTML portion of an email message, if available."""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/html":
                return part.get_payload(decode=True).decode(errors="ignore")

        # Fall back to plain text if there was no HTML part
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                return part.get_payload(decode=True).decode(errors="ignore")

    else:
        content_type = msg.get_content_type()
        if content_type in {"text/html", "text/plain"}:
            return msg.get_payload(decode=True).decode(errors="ignore")

    return None


def extract_jotform_link(html: str | None, stage_name: str | None = None) -> Optional[str]:
    """
    Extract any JotForm edit link from email HTML.
    The stage name (PCM, RD, etc.) is used to prioritise the correct link.
    """
    if not html:
        return None

    matches = LINK_PATTERN.findall(html)
    if not matches:
        return None

    stage_key = (stage_name or "").upper()
    if stage_key in STAGE_LINK_HINTS:
        hints = STAGE_LINK_HINTS[stage_key]
        for link in matches:
            if any(hint in link for hint in hints):
                return link.replace("&amp;", "&")

    # Fall back to returning the first match
    return matches[0].replace("&amp;", "&")


class GmailApprovalLinkRetriever:
    """Encapsulates IMAP logic required to poll Gmail for approval links."""

    def __init__(
        self,
        email_address: str = EMAIL_ADDRESS,
        app_password: str = APP_PASSWORD,
        imap_server: str = IMAP_SERVER,
        imap_folder: str = IMAP_FOLDER,
        sender_filter: str = SEARCH_SENDER,
    ):
        self.email_address = email_address
        self.app_password = app_password
        self.imap_server = imap_server
        self.imap_folder = imap_folder
        self.sender_filter = sender_filter
        self.mailbox: Optional[imaplib.IMAP4_SSL] = None

    # --------------------------------------------------------------------- #
    # Context management / connection helpers
    # --------------------------------------------------------------------- #
    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def connect(self):
        if self.mailbox is not None:
            return

        print("\n[EMAIL] Connecting to Gmail IMAP...")
        self.mailbox = imaplib.IMAP4_SSL(self.imap_server)
        self.mailbox.login(self.email_address, self.app_password)
        print("[EMAIL] Connected.")

    def close(self):
        if self.mailbox is not None:
            try:
                self.mailbox.logout()
            except Exception:
                pass
            finally:
                self.mailbox = None

    # --------------------------------------------------------------------- #
    # Internal helpers
    # --------------------------------------------------------------------- #
    def _select_folder(self):
        if self.mailbox is None:
            raise RuntimeError("Mailbox is not connected.")

        self.mailbox.select(self.imap_folder)

    def _search_messages(self, efs_ref: str) -> List[bytes]:
        """Search the mailbox for messages from the JotForm sender containing the EFS reference."""
        if self.mailbox is None:
            raise RuntimeError("Mailbox is not connected.")

        self._select_folder()

        sanitized_ref = efs_ref.replace('"', "")
        search_query = f'(FROM "{self.sender_filter}" BODY "{sanitized_ref}")'
        status, data = self.mailbox.search(None, search_query)

        if status != "OK":
            return []

        message_ids = data[0].split()
        return message_ids if message_ids else []

    def _fetch_message(self, msg_id: bytes) -> Optional[Message]:
        if self.mailbox is None:
            raise RuntimeError("Mailbox is not connected.")

        status, msg_data = self.mailbox.fetch(msg_id, "(RFC822)")
        if status != "OK" or not msg_data:
            return None

        raw_email = msg_data[0][1]
        return email.message_from_bytes(raw_email)

    # --------------------------------------------------------------------- #
    # Public API
    # --------------------------------------------------------------------- #
    def get_approval_link(
        self,
        stage_name: str,
        efs_ref: str,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
        poll_interval_seconds: int = POLL_INTERVAL_SECONDS,
    ) -> Optional[str]:
        """
        Poll Gmail for an approval email that contains the provided EFS reference.
        Returns the first matching JotForm edit link or None if no email arrives.
        """
        self.connect()

        end_time = time.time() + timeout_seconds
        attempt = 1

        try:
            while time.time() < end_time:
                print(f"[EMAIL] Attempt {attempt}: looking for {efs_ref} ({stage_name})")
                message_ids = self._search_messages(efs_ref)

                if message_ids:
                    # Process newest first
                    for msg_id in reversed(message_ids):
                        msg = self._fetch_message(msg_id)
                        if not msg:
                            continue

                        html_body = _extract_html_body(msg)
                        link = extract_jotform_link(html_body, stage_name)

                        if link:
                            print("[EMAIL] Approval link found in Gmail inbox.")
                            return link

                remaining = end_time - time.time()
                if remaining <= 0:
                    break

                wait_time = min(poll_interval_seconds, int(remaining))
                print(f"[EMAIL] No link yet. Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
                attempt += 1

            print("[EMAIL] Timeout waiting for Gmail approval email.")
            return None

        finally:
            self.close()


def get_approval_link_for_test(stage_name: str, efs_ref: str) -> Optional[str]:
    """
    Convenience wrapper used by the playwright test runner.  Returns a JotForm
    approval link for the given stage/EFS reference, or None when not available.
    """
    with GmailApprovalLinkRetriever() as retriever:
        return retriever.get_approval_link(stage_name, efs_ref)


if __name__ == "__main__":
    stage = input("Enter stage (PCM/RD/RCM): ").strip().upper() or "PCM"
    ref = input("Enter EFS reference: ").strip()

    if not ref:
        raise SystemExit("EFS reference is required.")

    link = get_approval_link_for_test(stage, ref)
    if link:
        print(f"\n[EMAIL] Link: {link}")
    else:
        print("\n[EMAIL] No approval link found.")
