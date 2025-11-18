"""
Test extract_efs_ref with the ACTUAL HTML from your thank you page
"""
try:
    from utils import extract_efs_ref
    print("✅ Imported extract_efs_ref from utils.py\n")
except ImportError:
    print("❌ Could not import utils.py")
    exit(1)

# The ACTUAL HTML from your thank you page
actual_html = """
<div class="thankyou-wrapper">
<div style="text-align:center;">
<h1 class="thankyou-main-text ty-text">Thank You!</h1>
<p class="thankyou-sub-text ty-text">EFS Ref:&nbsp;DEV_PR400</p>
<p class="thankyou-sub-text ty-text">This Form has been sent to George Warren.</p>
</div>
</div>
"""

print("="*70)
print("Testing with ACTUAL HTML from your thank you page")
print("="*70 + "\n")

# Test 1: With HTML entity (&nbsp;)
print("Test 1: With HTML entity (&nbsp;)")
result1 = extract_efs_ref(actual_html)
print(f"   Result: {result1}")
print(f"   Status: {'✅ PASS' if result1 == 'DEV_PR400' else '❌ FAIL'}")
print()

# Test 2: With regular space (how Playwright might return it)
html_with_space = actual_html.replace("&nbsp;", " ")
print("Test 2: With regular space (EFS Ref: DEV_PR400)")
result2 = extract_efs_ref(html_with_space)
print(f"   Result: {result2}")
print(f"   Status: {'✅ PASS' if result2 == 'DEV_PR400' else '❌ FAIL'}")
print()

# Test 3: With no space (EFS Ref:DEV_PR400)
html_no_space = "EFS Ref:DEV_PR400"
print("Test 3: With no space (EFS Ref:DEV_PR400)")
result3 = extract_efs_ref(html_no_space)
print(f"   Result: {result3}")
print(f"   Status: {'✅ PASS' if result3 == 'DEV_PR400' else '❌ FAIL'}")
print()

# Test 4: With actual non-breaking space character
html_with_nbsp_char = "EFS Ref:\u00A0DEV_PR400"
print("Test 4: With actual non-breaking space character")
result4 = extract_efs_ref(html_with_nbsp_char)
print(f"   Result: {result4}")
print(f"   Status: {'✅ PASS' if result4 == 'DEV_PR400' else '❌ FAIL'}")
print()

print("="*70)
if all([result1, result2, result3, result4]):
    print("✅ All tests passed! Your extract_efs_ref() handles all cases")
else:
    print("❌ Some tests failed!")
    print("\n💡 Your regex pattern needs to handle:")
    print("   - HTML entities (&nbsp;)")
    print("   - Regular spaces")
    print("   - No spaces")
    print("   - Non-breaking space characters (\\u00A0)")
    print("\nUpdate the pattern in utils.py to: r\"EFS\\s*Ref:?\\s*([A-Z0-9_]+)\"")
print("="*70)