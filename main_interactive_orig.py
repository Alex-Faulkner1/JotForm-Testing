"""
JotForm Payment Request Automation Script - INTERACTIVE VERSION
Fills forms and pauses for manual review before submission
"""
import asyncio
from playwright.async_api import async_playwright, Page
from utils import make_test_pdf, extract_efs_ref, extract_edit_link, create_output_folder
from config import (
    JOTFORM_URL, HEADLESS_MODE, BROWSER_TIMEOUT, TEST_DATA,
    EMAILS, WORKFLOW_WAIT_TIME, REDIRECT_TIMEOUT
)


def get_user_input():
    """Get user inputs at the start."""
    print("\n" + "="*60)
    print("JotForm Testing - Interactive Mode")
    print("="*60 + "\n")

    default_email = EMAILS.get("pcm_email", "your.email@digiblu.com")
    email = input(f"Enter your email [{default_email}]: ").strip()
    if not email:
        email = default_email

    print(f"\n✅ Using email: {email}")
    return {"email": email}


def wait_for_confirmation(message):
    """Wait for user confirmation."""
    print("\n" + "="*60)
    print(f"⏸️  PAUSED: {message}")
    print("="*60)
    response = input("Press ENTER to continue (or 'skip'): ").strip().lower()
    return response != 'skip'


async def check_already_reviewed(page: Page) -> bool:
    """
    Check if the form has already been reviewed.
    Returns True if already reviewed, False otherwise.
    """
    try:
        # Wait a moment for the banner to appear
        await page.wait_for_timeout(2000)

        # Look for the banner text
        banner_text = "You have already reviewed this Form"
        page_content = await page.content()

        if banner_text in page_content:
            print("\n" + "=" * 60)
            print("ℹ️  ALREADY REVIEWED")
            print("=" * 60)
            print("This form has already been reviewed.")
            print("No further action is required at this stage.")
            print("=" * 60 + "\n")
            return True

        return False

    except Exception as e:
        print(f"Warning: Error checking for banner: {e}")
        return False

async def wait_for_redirect(page: Page, initial_url: str, timeout: int = REDIRECT_TIMEOUT) -> bool:
    """Wait for redirect."""
    await page.wait_for_timeout(timeout)
    current_url = page.url

    if current_url == initial_url:
        print("Warning: No redirect. Retrying...")
        await page.click("#input_98")
        await page.wait_for_timeout(timeout)

        if page.url == initial_url:
            print("Error: No redirect after retry")
            return False

    print(f"Success: Redirected to {page.url}")
    return True


async def select_approver(page: Page) -> None:
    """Select approver from iframe."""
    try:
        await page.wait_for_timeout(3000)
        frames = page.frames

        ad_frames = [(i, f) for i, f in enumerate(frames)
                     if "ActiveDirectoryDropDown.html" in (f.url or "")]

        print(f"Found {len(ad_frames)} ActiveDirectory iframes")

        for frame_idx, frame in ad_frames:
            try:
                dropdown = await frame.query_selector("#input_ADDropdown")
                if dropdown:
                    await frame.wait_for_timeout(1000)
                    options = await dropdown.query_selector_all("option")

                    if len(options) > 1:
                        await frame.select_option("#input_ADDropdown",
                                                  value=await options[1].get_attribute("value"))
                        print(f"✅ Selected: {await options[1].text_content()}")
                        return
            except:
                continue

        print("⚠️  Could not select approver. Please select manually.")
    except Exception as e:
        print(f"⚠️  Error: {e}")


async def fill_inputter_stage(page: Page, user_email: str) -> None:
    """Fill Stage 1 form."""
    print("\n===== STAGE 1: INPUTTER STAGE =====")
    await page.goto(JOTFORM_URL)
    print("Navigated to form")

    await page.select_option("#input_123", label=TEST_DATA["company_division"])
    print("✓ Company / Division")

    await page.fill("#input_124", TEST_DATA["location_number"])
    print("✓ Location Number")

    await page.fill("#input_131", TEST_DATA["raised_by"])
    print("✓ Raised By")

    date_value = await page.input_value("#lite_mode_130")
    print(f"✓ Payment Request Date: {date_value}")

    await page.select_option("#input_543", label=TEST_DATA["payment_type"])
    print("✓ Payment Request Type")

    await page.fill("#input_701", TEST_DATA["description"])
    print("✓ Description")

    await page.fill("#input_547", TEST_DATA["payee"])
    print("✓ Payee")

    await page.click("#label_input_604_0")
    print("✓ Has invoice: Yes")

    await page.set_input_files("#input_558", TEST_DATA["invoice_filename"])
    print("✓ Uploaded PDF")

    await page.fill("#input_562", TEST_DATA["invoice_number"])
    print("✓ Invoice Number")

    await page.fill("#lite_mode_566", TEST_DATA["invoice_date"])
    print("✓ Invoice Date")

    await page.click("#label_input_607_0")
    print("✓ Bank details on invoice: Yes")

    await page.fill("#input_844", TEST_DATA["value"])
    print("✓ Value")

    await select_approver(page)

    await page.fill("#input_195", user_email)
    print(f"✓ PCM Email: {user_email}")


async def submit_inputter_stage(page: Page) -> tuple[str, str]:
    """Submit Stage 1."""
    initial_url = page.url
    await page.click("#input_98")
    print("Submit clicked...")

    if not await wait_for_redirect(page, initial_url):
        return None, None

    page_content = await page.content()
    efs_ref = extract_efs_ref(page_content)

    if not efs_ref:
        print("Error: Could not find EFS Ref")
        return None, None

    print(f"✅ EFS Ref: {efs_ref}")

    edit_link = extract_edit_link(page_content)
    if edit_link:
        print(f"✅ Next stage link found")

    return efs_ref, edit_link


async def process_pcm_stage(page: Page, pcm_url: str, output_folder: str, user_email: str) -> str:
    """Process PCM stage."""
    print("\n===== PCM STAGE =====")
    await page.goto(pcm_url)
    print("Navigated to PCM form")

    await page.wait_for_timeout(2000)

    # ADD THIS CHECK HERE (around line 175-180)
    if await check_already_reviewed(page):
        await page.screenshot(path=f"{output_folder}/pcm_already_reviewed.png")
        print("✅ Screenshot saved: pcm_already_reviewed.png")

        page_content = await page.content()
        next_url = extract_edit_link(page_content)

        if next_url:
            print(f"✅ Found next stage link")
            return next_url
        else:
            print("ℹ️  No next stage link found")
            return None

    # Continue with normal approval flow
    try:
        await page.wait_for_selector("#label_input_203_0", timeout=10000)
        await page.click("#label_input_203_0")
        print("✓ Selected: Approve")
    except Exception as e:
        print(f"Error: {e}")
        return None

    await page.fill("#input_244", user_email)
    print(f"✓ RD Email: {user_email}")

    if not wait_for_confirmation("Review PCM form before submitting"):
        print("⏭️  Skipped PCM")
        return None

    await page.click("#input_98")
    print("Submit clicked...")

    if not await wait_for_redirect(page, pcm_url):
        return None

    await page.screenshot(path=f"{output_folder}/pcm_stage_submitted.png")
    print("✅ Screenshot saved")

    return extract_edit_link(await page.content())


async def process_rd_stage(page: Page, rd_url: str, output_folder: str) -> bool:
    """Process RD stage."""
    print("\n===== RD STAGE =====")
    await page.goto(rd_url)
    print("Navigated to RD form")

    await page.wait_for_timeout(2000)

    try:
        await page.wait_for_selector("#label_input_249_0", timeout=10000)
        await page.click("#label_input_249_0")
        print("✓ Selected: Approve")
    except Exception as e:
        print(f"Error: {e}")
        return False

    if not wait_for_confirmation("Review RD form before submitting"):
        print("⏭️  Skipped RD")
        return False

    await page.click("#input_98")
    success = await wait_for_redirect(page, rd_url)

    await page.screenshot(path=f"{output_folder}/rd_stage_submitted.png")
    print("✅ Screenshot saved")

    return success


async def run_automation():
    """Main workflow."""
    user_inputs = get_user_input()
    user_email = user_inputs["email"]

    make_test_pdf(TEST_DATA["invoice_filename"])
    print(f"Generated PDF: {TEST_DATA['invoice_filename']}")

    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=HEADLESS_MODE)
        page = await browser.new_page()

        try:
            await fill_inputter_stage(page, user_email)

            print("\n" + "="*60)
            print("📋 Form filled! Review in browser.")
            print("="*60)

            if not wait_for_confirmation("Review and submit Stage 1"):
                print("⏭️  Exiting without submission")
                await page.screenshot(path="output/stage1_review.png")
                return

            efs_ref, pcm_url = await submit_inputter_stage(page)

            if not efs_ref or not pcm_url:
                print("Error: Stage 1 failed")
                return

            output_folder = create_output_folder(efs_ref)
            await page.screenshot(path=f"{output_folder}/stage1_submitted.png")
            print(f"✅ Output folder: {output_folder}")

            print(f"Waiting {WORKFLOW_WAIT_TIME/1000}s for workflows...")
            await page.wait_for_timeout(WORKFLOW_WAIT_TIME)

            rd_url = await process_pcm_stage(page, pcm_url, output_folder, user_email)

            if not rd_url:
                return

            print(f"Waiting {WORKFLOW_WAIT_TIME/1000}s for workflows...")
            await page.wait_for_timeout(WORKFLOW_WAIT_TIME)

            success = await process_rd_stage(page, rd_url, output_folder)

            if success:
                print("\n✅ ALL STAGES COMPLETED")

        except Exception as e:
            print(f"\n❌ Error: {e}")
            raise

        finally:
            print("\nBrowser closing in 5s...")
            await page.wait_for_timeout(5000)
            await browser.close()


if __name__ == "__main__":
    asyncio.run(run_automation())