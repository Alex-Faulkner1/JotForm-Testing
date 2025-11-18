"""
Debug Script - Capture Thank You Page HTML to Find EFS Reference
This will help us see exactly what's on the page after form submission
"""
import asyncio
from playwright.async_api import async_playwright
import re


async def debug_thank_you_page():
    """Submit a test form and capture the thank you page HTML."""

    try:
        from config import JOTFORM_URL
    except ImportError:
        JOTFORM_URL = input("Enter your JotForm URL: ").strip()

    print("\n" + "=" * 70)
    print("Thank You Page Debug - Finding EFS Reference")
    print("=" * 70)
    print("This will submit a test form and show you what's on the thank you page")
    print("=" * 70 + "\n")

    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=False)
        page = await browser.new_page()

        try:
            print("1️⃣  Loading form...")
            await page.goto(JOTFORM_URL)
            await page.wait_for_timeout(3000)
            print("✅ Form loaded")

            print("\n2️⃣  Fill out a minimal test form manually")
            print("   Then press ENTER here when you've submitted it...")
            input()

            # Wait for redirect
            print("\n3️⃣  Waiting for thank you page...")
            await page.wait_for_timeout(3000)

            current_url = page.url
            print(f"✅ Current URL: {current_url}")

            # Get the full page content
            print("\n4️⃣  Capturing page HTML...")
            html_content = await page.content()

            # Save to file
            with open("thank_you_page_debug.html", "w", encoding="utf-8") as f:
                f.write(html_content)
            print("✅ Saved full HTML to: thank_you_page_debug.html")

            # Get visible text
            print("\n5️⃣  Getting visible text on page...")
            body_text = await page.inner_text("body")

            print("\n" + "=" * 70)
            print("VISIBLE TEXT ON PAGE:")
            print("=" * 70)
            print(body_text)
            print("=" * 70)

            # Try to find EFS reference patterns
            print("\n6️⃣  Searching for EFS Reference patterns...")

            patterns = [
                (r"DEV_PR\d+", "DEV_PR### format"),
                (r"EFS[- ]?\d{6}", "EFS-###### format"),
                (r"Reference:?\s*([A-Z0-9_-]+)", "Reference: ... format"),
                (r"Ref:?\s*([A-Z0-9_-]+)", "Ref: ... format"),
                (r"\b[A-Z]{3}_[A-Z]{2}\d+\b", "XXX_YY### format"),
            ]

            found_any = False
            for pattern, description in patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                if matches:
                    found_any = True
                    print(f"\n✅ Found with {description}:")
                    for match in set(matches):
                        print(f"   - {match}")

            if not found_any:
                print("\n❌ No EFS Reference patterns found!")
                print("\n🔍 Let's check what we DO have...")

                # Look for common words that might indicate where ref would be
                keywords = ["reference", "ref", "number", "id", "submission", "form"]
                for keyword in keywords:
                    if keyword.lower() in body_text.lower():
                        # Find context around the keyword
                        idx = body_text.lower().find(keyword.lower())
                        context = body_text[max(0, idx - 50):min(len(body_text), idx + 100)]
                        print(f"\nFound '{keyword}': ...{context}...")

            # Check for the submission ID in URL
            print("\n7️⃣  Checking URL for submission ID...")
            url_pattern = r"/submit/(\d+)"
            url_match = re.search(url_pattern, current_url)
            if url_match:
                submission_id = url_match.group(1)
                print(f"✅ Found submission ID in URL: {submission_id}")
                print(f"   Full URL: {current_url}")

            print("\n" + "=" * 70)
            print("DEBUGGING SUMMARY")
            print("=" * 70)
            print("1. Check 'thank_you_page_debug.html' for full HTML")
            print("2. Look at the visible text above")
            print("3. See if any patterns matched")
            print("4. Note the submission ID from URL")
            print("=" * 70)

            print("\n💡 Keeping browser open for 30 seconds for inspection...")
            await page.wait_for_timeout(30000)

        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()

            await page.wait_for_timeout(30000)

        finally:
            await browser.close()

    print("\n" + "=" * 70)
    print("Debug Complete")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Review the visible text above")
    print("2. Open 'thank_you_page_debug.html' in a browser")
    print("3. Look for the EFS Reference format")
    print("4. Share what you find so we can update the pattern")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(debug_thank_you_page())