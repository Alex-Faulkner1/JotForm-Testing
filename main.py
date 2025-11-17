"""
JotForm Payment Request Automation Script
Automates the multi-stage approval workflow for payment requests
"""
import asyncio
from playwright.async_api import async_playwright, Page
from utils import make_test_pdf, extract_efs_ref, extract_edit_link, create_output_folder
from config import (
    JOTFORM_URL, HEADLESS_MODE, BROWSER_TIMEOUT, TEST_DATA, 
    EMAILS, WORKFLOW_WAIT_TIME, REDIRECT_TIMEOUT
)


async def wait_for_redirect(page: Page, initial_url: str, timeout: int = REDIRECT_TIMEOUT) -> bool:
    """
    Wait for page redirect and retry if necessary.
    
    Args:
        page: Playwright page object
        initial_url: URL before submission
        timeout: Time to wait for redirect in milliseconds
    
    Returns:
        bool: True if redirect successful, False otherwise
    """
    await page.wait_for_timeout(timeout)
    current_url = page.url
    
    if current_url == initial_url:
        print("Warning: No redirect detected. Retrying submit...")
        await page.click("#input_98")
        await page.wait_for_timeout(timeout)
        
        current_url = page.url
        if current_url == initial_url:
            print("Error: Still no redirect after retry")
            return False
        else:
            print(f"Success: Redirected to {current_url}")
            return True
    else:
        print(f"Success: Redirected to {current_url}")
        return True


async def fill_inputter_stage(page: Page) -> None:
    """
    Fill out the Inputter (Stage 1) form fields.
    
    Args:
        page: Playwright page object
    """
    print("\n===== STAGE 1: INPUTTER STAGE =====")
    await page.goto(JOTFORM_URL)
    print("Navigated to form")

    # 1. Company / Division
    await page.select_option("#input_123", label=TEST_DATA["company_division"])
    print("Completed: Company / Division")

    # 2. Location Number
    await page.fill("#input_124", TEST_DATA["location_number"])
    print("Completed: Location Number")

    # 3. Raised By
    await page.fill("#input_131", TEST_DATA["raised_by"])
    print("Completed: Raised By")

    # 4. Payment Request Date - confirm it has a value
    date_value = await page.input_value("#lite_mode_130")
    if date_value:
        print(f"Completed: Payment Request Date has value: {date_value}")
    else:
        print("Warning: Payment Request Date is empty")

    # 5. Payment Request Type
    await page.select_option("#input_543", label=TEST_DATA["payment_type"])
    print("Completed: Payment Request Type")

    # 6. Description
    await page.fill("#input_701", TEST_DATA["description"])
    print("Completed: Description")

    # 7. Payee
    await page.fill("#input_547", TEST_DATA["payee"])
    print("Completed: Payee")

    # 8. Do you have an invoice? -> Yes
    if TEST_DATA["has_invoice"]:
        await page.click("#label_input_604_0")
        print("Completed: Do you have an invoice? (Yes)")

    # 9. Upload PDF file
    await page.set_input_files("#input_558", TEST_DATA["invoice_filename"])
    print("Completed: Upload PDF file")

    # 10. Invoice Number
    await page.fill("#input_562", TEST_DATA["invoice_number"])
    print("Completed: Invoice Number")

    # 11. Invoice Date
    await page.fill("#lite_mode_566", TEST_DATA["invoice_date"])
    print("Completed: Invoice Date")

    # 12. Bank Account Details on invoice? -> Yes
    if TEST_DATA["bank_details_on_invoice"]:
        await page.click("#label_input_607_0")
        print("Completed: Bank Account Details on invoice? (Yes)")

    # 13. Value
    await page.fill("#input_844", TEST_DATA["value"])
    print("Completed: Value")

    # 14. Profit Centre Manager Approver (iframe handling)
    await select_approver(page)

    # 15. Profit Centre Manager Email
    await page.fill("#input_195", EMAILS["pcm_email"])
    print("Completed: Profit Centre Manager Email")


async def select_approver(page: Page) -> None:
    """
    Select the approver from dropdown in iframe.
    
    Args:
        page: Playwright page object
    """
    frame = None
    for f in page.frames:
        if "ADDropdown" in (f.name or "") or "ADDropdown" in f.url:
            frame = f
            break

    if frame:
        dropdown = await frame.query_selector("#input_ADDropdown")
        if dropdown:
            options = await dropdown.query_selector_all("option")
            if len(options) > 1:
                second_value = await options[1].get_attribute("value")
                await frame.select_option("#input_ADDropdown", value=second_value)
                approver_text = await options[1].text_content()
                print(f"Completed: Profit Centre Manager Approver - Selected: {approver_text}")
            else:
                print("Warning: No second option found in approver dropdown")
        else:
            print("Warning: Approver dropdown not found in iframe")
    else:
        print("Warning: Approver dropdown iframe not found.")


async def submit_inputter_stage(page: Page) -> tuple[str, str]:
    """
    Submit the inputter stage and extract EFS reference and next stage URL.
    
    Args:
        page: Playwright page object
    
    Returns:
        tuple: (efs_ref, next_stage_url) or (None, None) if failed
    """
    initial_url = page.url
    await page.click("#input_98")
    print("Completed: Submit button clicked")

    # Wait for redirect
    if not await wait_for_redirect(page, initial_url):
        return None, None

    # Extract EFS Ref and edit link
    page_content = await page.content()
    efs_ref = extract_efs_ref(page_content)
    
    if not efs_ref:
        print("Error: Could not find EFS Ref on thank you page")
        return None, None
    
    print(f"Found EFS Ref: {efs_ref}")
    
    edit_link = extract_edit_link(page_content)
    if not edit_link:
        print("Error: Could not find edit link for next stage")
        return efs_ref, None
    
    print(f"Found next stage edit link: {edit_link}")
    return efs_ref, edit_link


async def process_pcm_stage(page: Page, pcm_url: str, output_folder: str) -> str:
    """
    Process the Profit Centre Manager (PCM) approval stage.
    
    Args:
        page: Playwright page object
        pcm_url: URL for the PCM stage form
        output_folder: Path to save screenshots
    
    Returns:
        str: URL for the next stage or None if failed
    """
    print("\n===== PCM STAGE =====")
    await page.goto(pcm_url)
    print("Navigated to PCM Stage form")

    # Profit Centre Manager Approve or Reject -> Approve
    await page.click("#label_input_203_0")
    print("Completed: Profit Centre Manager Approve or Reject (Approve)")

    # Regional Director Email for Testing
    await page.fill("#input_244", EMAILS["rd_email"])
    print("Completed: Regional Director Email for Testing")

    # Submit PCM Stage
    initial_url = page.url
    await page.click("#input_98")
    print("Completed: PCM Stage Submit button clicked")

    if not await wait_for_redirect(page, initial_url):
        return None

    await page.screenshot(path=f"{output_folder}/pcm_stage_submitted.png")
    print("PCM Stage screenshot saved.")

    # Extract next stage URL
    page_content = await page.content()
    next_url = extract_edit_link(page_content)
    
    if not next_url:
        print("Error: Could not find edit link for RD Stage")
        return None
    
    print(f"Found RD Stage edit link: {next_url}")
    return next_url


async def process_rd_stage(page: Page, rd_url: str, output_folder: str) -> bool:
    """
    Process the Regional Director (RD) approval stage.
    
    Args:
        page: Playwright page object
        rd_url: URL for the RD stage form
        output_folder: Path to save screenshots
    
    Returns:
        bool: True if successful, False otherwise
    """
    print("\n===== RD STAGE =====")
    await page.goto(rd_url)
    print("Navigated to RD Stage form")

    # Regional Director Approve or Reject -> Approve
    await page.click("#label_input_249_0")
    print("Completed: Regional Director Approve or Reject (Approve)")

    # Submit RD Stage
    initial_url = page.url
    await page.click("#input_98")
    print("Completed: RD Stage Submit button clicked")

    success = await wait_for_redirect(page, initial_url)
    
    await page.screenshot(path=f"{output_folder}/rd_stage_submitted.png")
    print("RD Stage screenshot saved.")
    
    return success


async def run_automation():
    """
    Main automation workflow that orchestrates all stages.
    """
    # Generate test PDF
    make_test_pdf(TEST_DATA["invoice_filename"])
    print(f"Generated test PDF: {TEST_DATA['invoice_filename']}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=HEADLESS_MODE)
        page = await browser.new_page()
        
        try:
            # Stage 1: Inputter
            await fill_inputter_stage(page)
            efs_ref, pcm_url = await submit_inputter_stage(page)
            
            if not efs_ref or not pcm_url:
                print("Error: Failed to complete Inputter stage")
                return
            
            # Create output folder
            output_folder = create_output_folder(efs_ref)
            print(f"Created output folder: {output_folder}")
            
            # Save Stage 1 screenshot
            await page.screenshot(path=f"{output_folder}/stage1_submitted.png")
            print("Stage 1 screenshot saved.")
            
            # Wait for background workflows
            print(f"Waiting {WORKFLOW_WAIT_TIME/1000} seconds for background workflows...")
            await page.wait_for_timeout(WORKFLOW_WAIT_TIME)
            
            # Stage 2: PCM
            rd_url = await process_pcm_stage(page, pcm_url, output_folder)
            
            if not rd_url:
                print("Error: Failed to complete PCM stage")
                return
            
            # Wait for background workflows
            print(f"Waiting {WORKFLOW_WAIT_TIME/1000} seconds for background workflows...")
            await page.wait_for_timeout(WORKFLOW_WAIT_TIME)
            
            # Stage 3: RD
            success = await process_rd_stage(page, rd_url, output_folder)
            
            if success:
                print("\n===== ALL STAGES COMPLETED SUCCESSFULLY =====")
                print(f"All screenshots saved in folder: {output_folder}")
            else:
                print("\n===== WORKFLOW COMPLETED WITH ERRORS =====")
                print(f"Screenshots saved in folder: {output_folder}")
        
        except Exception as e:
            print(f"\nError during automation: {str(e)}")
            raise
        
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(run_automation())
