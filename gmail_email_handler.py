import imaplib
import email
import re

# =========================
# CONFIGURATION
# =========================
IMAP_SERVER = "imap.gmail.com"

EMAIL_ADDRESS = "mustapha.jobe0001@gmail.com"
APP_PASSWORD = "nuho iurm uepl klem"

SEARCH_SENDER = "noreply@formresponse.com"
UNIQUE_ID = "DEV_PR403"

# =========================
# Connect to IMAP
# =========================
print("\n[INFO] Connecting to Gmail IMAP...")
mail = imaplib.IMAP4_SSL(IMAP_SERVER)

try:
    mail.login(EMAIL_ADDRESS, APP_PASSWORD)
except:
    print("[ERROR] Login failed. Check your App Password.")
    raise

mail.select("inbox")


# =========================
# Search emails
# =========================
print(f"[INFO] Searching emails from '{SEARCH_SENDER}' with '{UNIQUE_ID}'...")

search_query = f'(FROM "{SEARCH_SENDER}" BODY "{UNIQUE_ID}")'
result, data = mail.search(None, search_query)

if result != "OK":
    print("No messages found.")
    exit()

email_ids = data[0].split()

if not email_ids:
    print("[INFO] No matching emails found.")
    exit()

print(f"[INFO] Found {len(email_ids)} matching email(s). Scanning...\n")


# =========================
# Helper to extract Jotform link
# =========================
def extract_jotform_link(html: str) -> str | None:
    """
    Extract any JotForm edit link from email HTML, no stage names needed.
    Auto-detects all ?xxxxx codes.
    """
    pattern = r"https://eel\.jotform\.com/edit/\d+\?[A-Za-z0-9]+"
    match = re.search(pattern, html)
    return match.group(0) if match else None


# =========================
# Loop through matched emails
# =========================
found_link = False

for msg_id in email_ids:
    result, msg_data = mail.fetch(msg_id, "(RFC822)")
    raw_email = msg_data[0][1]

    msg = email.message_from_bytes(raw_email)

    # Extract HTML or plain text content
    html_body = None

    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                html_body = part.get_payload(decode=True).decode(errors="ignore")
                break
    else:
        # Non-multipart email
        if msg.get_content_type() == "text/html":
            html_body = msg.get_payload(decode=True).decode(errors="ignore")

    # If HTML exists, scan for link
    if html_body:
        link = extract_jotform_link(html_body)
        if link:
            print("[FOUND JOTFORM LINK]:", link)
            found_link = True
            break

if not found_link:
    print("[INFO] No Jotform link found in the matched emails.")
