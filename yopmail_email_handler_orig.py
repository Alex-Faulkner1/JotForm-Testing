import uuid
import os
import re
import time
from yopmail import Yopmail

# ================================================================
# Save & Load Email from File
# ================================================================
def save_email(email, filename="yopmail_address.txt"):
    with open(filename, "w") as f:
        f.write(email)
    print(f"[INFO] Saved generated email to {filename} (reference only)")


def load_email(filename="yopmail_address.txt"):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return f.read().strip()
    return None


# ================================================================
# Generate a secure, unguessable YOPmail address
# ================================================================
def generate_secure_yopmail():
    return f"{uuid.uuid4().hex}@yopmail.com"


# ================================================================
# Extract Jotform signing link from email body
# ================================================================
def extract_jotform_link(html):
    pattern = r"(https://eel\.jotform\.com/edit/\d+\?[A-Za-z0-9]+)"
    match = re.search(pattern, html)
    return match.group(1) if match else None


# ================================================================
# User Menu + Mailbox Selection
# ================================================================
print("\n----- YOPMAIL EMAIL HANDLER -----\n")
print("1 = Create new unguessable YOPmail")
print("2 = Use your own email (or load saved one)\n")

choice = input("Enter option 1 or 2: ").strip()


# -------------------------------
# OPTION 1 – Create new mailbox
# -------------------------------
if choice == "1":
    email = generate_secure_yopmail()
    save_email(email)  # Save for reference only
    print(f"[NEW EMAIL CREATED]: {email}")

# -------------------------------
# OPTION 2 – User enters mailbox
# -------------------------------
elif choice == "2":
    manual = input("Enter a YOPmail address (or press ENTER to load saved one): ").strip()

    if manual:
        email = manual
    else:
        email = load_email()
        if not email:
            print("[WARNING] No saved email found → creating a new one.")
            email = generate_secure_yopmail()
            save_email(email)

    print(f"[USING EMAIL]: {email}")

# -------------------------------
# INVALID INPUT
# -------------------------------
else:
    raise ValueError("Invalid selection. Enter either 1 or 2.")


# ================================================================
# Normalize mailbox for Yopmail()
# ================================================================
mailbox_name = email.split("@")[0].strip().lower()

print(f"\n[INFO] Instantiating Yopmail for mailbox: '{mailbox_name}'\n")

yp = Yopmail(mailbox_name, proxies=None)


# ================================================================
# Retrieve inbox with polling (retry mechanism)
# ================================================================
print("[INFO] Checking inbox with polling (max 60 seconds)...")

max_attempts = 12  # 12 attempts × 5 seconds = 60 seconds total
attempt = 0
mail_ids = []

while attempt < max_attempts:
    attempt += 1
    print(f"[ATTEMPT {attempt}/{max_attempts}] Fetching emails...")

    # Scan first 5 pages
    temp_ids = []
    for page in range(1, 6):
        ids = yp.get_mail_ids(page=page)
        if ids:
            temp_ids.extend(ids)

    if temp_ids:
        mail_ids = temp_ids
        print(f"[SUCCESS] Found {len(mail_ids)} email(s)!")
        break

    if attempt < max_attempts:
        print("[INFO] No emails yet, waiting 5 seconds...")
        time.sleep(5)

if not mail_ids:
    print("\n[INFO] No emails found after polling. The email might not have arrived yet.")
    print(f"[TIP] Check manually at: https://yopmail.com/?login={mailbox_name}")
else:
    print(f"\n[INFO] Scanning {len(mail_ids)} email(s) for Jotform link...\n")

    found_link = False

    for mail_id in mail_ids:
        try:
            mail = yp.get_mail_body(mail_id, show_image=True)
            html_body = getattr(mail, "body", "")

            link = extract_jotform_link(html_body)
            if link:
                print(f"[FOUND JOTFORM LINK]: {link}")
                found_link = True
                break  # Stop after finding first link
        except Exception as e:
            print(f"[WARNING] Error reading mail {mail_id}: {e}")
            continue

    if not found_link:
        print("[INFO] No Jotform signing link found in inbox.")