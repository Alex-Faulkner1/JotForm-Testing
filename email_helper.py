"""
Email helper functions for reading approval emails
"""
import re
import time
from imapclient import IMAPClient
from email import message_from_bytes
from email.header import decode_header


def connect_to_email(email_address: str, password: str, imap_server: str, imap_port: int):
    """Connect to email via IMAP."""
    try:
        client = IMAPClient(imap_server, port=imap_port, use_uid=True, ssl=True)
        client.login(email_address, password)
        print(f"✅ Connected to email: {email_address}")
        return client
    except Exception as e:
        print(f"❌ Failed to connect to email: {e}")
        return None


def extract_approval_link(email_body: str) -> str:
    """
    Extract the approval link from email body.
    Looks for JotForm edit links with approval parameters.
    """
    # Pattern for JotForm approval links
    patterns = [
        r'https://eel\.jotform\.com/edit/\d+\?eapeo\d+e[^\s<>"\']*',
        r'href="(https://eel\.jotform\.com/edit/[^"]+)"',
    ]

    for pattern in patterns:
        match = re.search(pattern, email_body, re.IGNORECASE)
        if match:
            link = match.group(1) if 'href' in pattern else match.group(0)
            # Clean up any HTML encoding
            link = link.replace('&amp;', '&')
            return link

    return None


def search_approval_email(client, efs_ref: str, stage_name: str, timeout: int = 60):
    """
    Search for approval email by EFS reference.
    Waits up to timeout seconds for the email to arrive.
    """
    print(f"\n🔍 Searching for {stage_name} approval email...")
    print(f"   EFS Ref: {efs_ref}")
    print(f"   Timeout: {timeout} seconds")

    client.select_folder('INBOX')

    start_time = time.time()
    check_interval = 5  # Check every 5 seconds

    while (time.time() - start_time) < timeout:
        # Search for recent emails with EFS ref in subject
        messages = client.search(['SUBJECT', efs_ref, 'UNSEEN'])

        if messages:
            print(f"   Found {len(messages)} unread email(s) with EFS ref")

            # Get the most recent message
            msg_id = messages[-1]

            # Fetch the email
            raw_message = client.fetch([msg_id], ['RFC822'])
            email_message = message_from_bytes(raw_message[msg_id][b'RFC822'])

            # Get email body
            body = ""
            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        break
                    elif part.get_content_type() == "text/html":
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
            else:
                body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')

            # Extract approval link
            approval_link = extract_approval_link(body)

            if approval_link:
                print(f"✅ Found approval link in email")
                return approval_link

        # Wait before checking again
        remaining = timeout - (time.time() - start_time)
        if remaining > 0:
            wait_time = min(check_interval, remaining)
            print(f"   Waiting {wait_time:.0f}s... ({remaining:.0f}s remaining)")
            time.sleep(wait_time)

    print(f"⏱️  Timeout: No approval email found after {timeout} seconds")
    return None


def get_approval_link_from_email(efs_ref: str, stage_name: str, email_config: dict) -> str:
    """
    Main function to get approval link from email.
    """
    email_address = email_config.get("email")
    password = email_config.get("password")

    # Prompt for password if not set
    if not password:
        import getpass
        password = getpass.getpass(f"Enter password for {email_address}: ")

    # Connect to email
    client = connect_to_email(
        email_address,
        password,
        email_config["imap_server"],
        email_config["imap_port"]
    )

    if not client:
        return None

    try:
        # Search for approval email
        approval_link = search_approval_email(
            client,
            efs_ref,
            stage_name,
            email_config.get("search_timeout", 60)
        )

        return approval_link

    finally:
        client.logout()
