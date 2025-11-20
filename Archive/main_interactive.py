"""
JotForm Payment Request Automation - MANUAL LINK VERSION
Fills forms and prompts for approval links from emails
Use this version when email approval links need to be manually entered
"""
import asyncio
from playwright.async_api import async_playwright, Page
from utils import make_test_pdf, extract_efs_ref, extract_edit_link, create_output_folder
from config import (
    JOTFORM_URL, HEADLESS_MODE, BROWSER_TIMEOUT, TEST_DATA,
    EMAILS, WORKFLOW_WAIT_TIME, REDIRECT_TIMEOUT
)
from email_helper import get_approval_link_from_email
from config import EMAIL_CONFIG

def get_user_input():
    """Get user inputs at the start."""
    print("\n" + "=" * 60)
    print("JotForm Testing - Manual Link Entry Mode")
    print("=" * 60 + "\n")

    default_email = EMAILS.get("pcm_email", "your.email@digiblu.com")
    email = input(f"Enter your email [{default_email}]: ").strip()
    if not email:
        email = default_email

    print(f"\n✅ Using email: {email}")
    return {"email": email}


def wait_for_confirmation(message):
    """Wait for user confirmation."""
    print("\n" + "=" * 60)
    print(f"⏸️  PAUSED: {message}")
    print("=" * 60)
    response = input("Press ENTER to continue (or 'skip'): ").strip().lower()
    return response != 'skip'


def get_approval_link_from_user(stage_name: str, efs_ref: str) -> str:
    """Prompt user to paste the approval link from their email."""
    print("\n" + "=" * 60)
    print(f"📧 {stage_name} Approval Link Required")
    print("=" * 60)
    print(f"EFS Ref: {efs_ref}")
    print(f"\nPlease check your email for the {stage_name} approval email.")
    print("Look for an email with subject containing the EFS Ref above.")
    print("Click 'Click here' in the email or copy the approval link.")
    print("The link should look like:")
    if stage_name == "PCM":
        print("  PCM: https://eel.jotform.com/edit/############?eapeo1e")
    elif stage_name == "RD":
        print("  RD:  https://eel.jotform.com/edit/############?eapet2e")
    else:
        print("  https://eel.jotform.com/edit/############?eape...")
    print("=" * 60 + "\n")

    while True:
        link = input(f"Paste the {stage_name} approval link (or 'skip' to end): ").strip()

        if link.lower() == 'skip':
            print(f"⏭️  Skipped {stage_name} stage")
            return None

        if not link:
            print("❌ No link provided. Please try again.")
            continue

        if "eel.jotform.com/edit/" in link:
            print(f"✅ Link received")
            return link
        else:
            print("⚠️  Link doesn't look like a JotForm approval link. Try again.")
            print("   Expected format: https://eel.jotform.com/edit/...")


async def check_already_reviewed(page: Page, stage_name: str = "Form") -> bool:
    """
    Check if the form has already been reviewed.
    Strategy: Check for approval buttons FIRST - if they exist, form needs approval.
    Only check for banner if no approval buttons found.

    Returns True if already reviewed, False if needs approval.
    """
    try:
        await page.wait_for_timeout(2000)

        print(f"[DEBUG] Checking if {stage_name} form is already reviewed...")

        # STEP 1: Check if approval buttons exist (if yes, form needs approval)
        approval_selectors = [
            "input[type='radio'][value='Approve']",
            "input[type='radio'][value='Reject']",
            "#label_input_203_0",  # PCM approve label
            "#label_input_249_0",  # RD approve label
        ]

        for selector in approval_selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    is_visible = await element.is_visible()
                    if is_visible:
                        print(f"[DEBUG] ✓ Found visible approval button - Form NEEDS approval")
                        return False  # Form needs approval
            except:
                continue

        print("[DEBUG] No approval buttons found - checking for 'already reviewed' banner...")

        # STEP 2: Check for "already reviewed" banner
        banner_selectors = [
            "text=You have already reviewed this Form",
            "text=No further action is required at this stage",
        ]

        for selector in banner_selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    is_visible = await element.is_visible()
                    if is_visible:
                        print(f"[DEBUG] ✓ Found 'already reviewed' banner")
                        print("\n" + "=" * 60)
                        print("ℹ️  ALREADY REVIEWED")
                        print("=" * 60)
                        print("This form has already been reviewed.")
                        print("No further action is required at this stage.")
                        print("=" * 60 + "\n")
                        return True
            except:
                continue

        print("[DEBUG] No banner found - Form likely NEEDS approval")
        return False

    except Exception as e:
        print(f"[DEBUG] Error in check_already_reviewed: {e}")
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
    return efs_ref, None


async def process_pcm_stage(page: Page, pcm_url: str, output_folder: str, user_email: str) -> str:
    """Process PCM stage."""
    print("\n===== PCM STAGE =====")
    await page.goto(pcm_url)
    print("Navigated to PCM form")

    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(2000)

    # Check if already reviewed
    if await check_already_reviewed(page, "PCM"):
        await page.screenshot(path=f"{output_folder}/pcm_already_reviewed.png")
        print("✅ Screenshot saved: pcm_already_reviewed.png")
        return "already_reviewed"

    # Form needs approval
    print("[DEBUG] Proceeding with approval...")
    try:
        await page.wait_for_selector("#label_input_203_0", timeout=10000)
        await page.click("#label_input_203_0")
        print("✓ Selected: Approve")
    except Exception as e:
        print(f"❌ Error clicking approve: {e}")
        await page.screenshot(path=f"{output_folder}/pcm_error.png")
        return None

    try:
        await page.fill("#input_244", user_email)
        print(f"✓ RD Email: {user_email}")
    except Exception as e:
        print(f"Warning: Could not fill RD email: {e}")

    if not wait_for_confirmation("Review PCM form before submitting"):
        print("⏭️  Skipped PCM submission")
        return None

    await page.click("#input_98")
    print("Submit clicked...")

    if not await wait_for_redirect(page, pcm_url):
        return None

    await page.screenshot(path=f"{output_folder}/pcm_stage_submitted.png")
    print("✅ Screenshot saved: pcm_stage_submitted.png")
    return "submitted"


async def process_rd_stage(page: Page, rd_url: str, output_folder: str) -> bool:
    """Process RD stage."""
    print("\n===== RD STAGE =====")
    await page.goto(rd_url)
    print("Navigated to RD form")

    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(2000)

    # Check if already reviewed
    if await check_already_reviewed(page, "RD"):
        await page.screenshot(path=f"{output_folder}/rd_already_reviewed.png")
        print("✅ Screenshot saved: rd_already_reviewed.png")
        return True

    # Form needs approval
    print("[DEBUG] Proceeding with approval...")
    try:
        await page.wait_for_selector("#label_input_249_0", timeout=10000)
        await page.click("#label_input_249_0")
        print("✓ Selected: Approve")
    except Exception as e:
        print(f"❌ Error clicking approve: {e}")
        await page.screenshot(path=f"{output_folder}/rd_error.png")
        return False

    if not wait_for_confirmation("Review RD form before submitting"):
        print("⏭️  Skipped RD submission")
        return False

    await page.click("#input_98")
    print("Submit clicked...")

    success = await wait_for_redirect(page, rd_url)

    await page.screenshot(path=f"{output_folder}/rd_stage_submitted.png")
    print("✅ Screenshot saved: rd_stage_submitted.png")
    return success


async def run_automation():
    """Main workflow with manual link entry."""
    user_inputs = get_user_input()
    user_email = user_inputs["email"]

    make_test_pdf(TEST_DATA["invoice_filename"])
    print(f"Generated PDF: {TEST_DATA['invoice_filename']}")

    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=HEADLESS_MODE)
        page = await browser.new_page()

        try:
            # STAGE 1: INPUTTER
            await fill_inputter_stage(page, user_email)

            print("\n" + "=" * 60)
            print("📋 Form filled! Review in browser.")
            print("=" * 60)

            if not wait_for_confirmation("Review and submit Stage 1"):
                print("⏭️  Exiting without submission")
                await page.screenshot(path="output/stage1_review.png")
                return

            efs_ref, pcm_url = await submit_inputter_stage(page)

            if not efs_ref:
                print("Error: Stage 1 failed")
                return

            # Try to get PCM link from email
            if not pcm_url:
                print("\n⏰ Waiting for PCM approval email...")
                pcm_url = get_approval_link_from_email(efs_ref, "PCM", EMAIL_CONFIG)

                # Fallback to manual input
                if not pcm_url:
                    pcm_url = get_approval_link_from_user("PCM", efs_ref)

                if not pcm_url:
                    print("Cannot proceed without PCM link")
                    return

            output_folder = create_output_folder(efs_ref)
            await page.screenshot(path=f"{output_folder}/stage1_submitted.png")
            print(f"✅ Output folder: {output_folder}")

            # GET PCM LINK
            print("\n" + "=" * 60)
            print("📧 Check your email for PCM approval")
            print("=" * 60)

            pcm_url = get_approval_link_from_user("PCM", efs_ref)

            if not pcm_url:
                print("⏭️  Workflow ended - no PCM link provided")
                return

            print(f"\nWaiting {WORKFLOW_WAIT_TIME / 1000}s for background workflows...")
            await page.wait_for_timeout(WORKFLOW_WAIT_TIME)

            # STAGE 2: PCM
            pcm_result = await process_pcm_stage(page, pcm_url, output_folder, user_email)

            if not pcm_result:
                print("⏭️  PCM stage ended")
                return

            # GET RD LINK
            print("\n" + "=" * 60)
            print("📧 Check your email for RD approval")
            print("=" * 60)

            rd_url = get_approval_link_from_user("RD", efs_ref)

            if not rd_url:
                print("⏭️  Workflow ended - no RD link provided")
                return

            print(f"\nWaiting {WORKFLOW_WAIT_TIME / 1000}s for background workflows...")
            await page.wait_for_timeout(WORKFLOW_WAIT_TIME)

            # STAGE 3: RD
            success = await process_rd_stage(page, rd_url, output_folder)

            if success:
                print("\n" + "=" * 60)
                print("✅ ALL STAGES COMPLETED SUCCESSFULLY")
                print("=" * 60)
                print(f"📁 Screenshots saved in: {output_folder}")
                print("=" * 60 + "\n")
            else:
                print("\n⚠️  Workflow completed with some stages skipped")

        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()

        finally:
            print("\n⏸️  Browser will close in 5 seconds...")
            await page.wait_for_timeout(5000)
            await browser.close()


if __name__ == "__main__":
    print("\n" + "🚀" * 30)
    print("  JotForm Testing - Manual Link Entry Mode")
    print("  You will be prompted to paste approval links from emails")
    print("🚀" * 30 + "\n")

    asyncio.run(run_automation())