"""
Quick test to verify utils.py extract_efs_ref() handles DEV_PR format
"""

# Test HTML content similar to what JotForm returns
test_html_samples = [
    # Format 1: Your DEV_PR format
    """
    <div>
        <h2>Thank You!</h2>
        <p>Your form has been submitted.</p>
        <p>EFS Reference: DEV_PR395</p>
    </div>
    """,

    # Format 2: Standard numeric format
    """
    <div>
        <h2>Thank You!</h2>
        <p>Your form has been submitted.</p>
        <p>EFS Reference: EFS-123456</p>
    </div>
    """,

    # Format 3: With "Ref:" label
    """
    <div>
        <h2>Thank You!</h2>
        <p>EFS Ref: DEV_PR400</p>
    </div>
    """,
]

print("=" * 60)
print("Testing utils.py extract_efs_ref() function")
print("=" * 60)

try:
    from utils import extract_efs_ref

    for i, html in enumerate(test_html_samples, 1):
        result = extract_efs_ref(html)
        expected = ["DEV_PR395", "EFS-123456", "DEV_PR400"][i - 1]

        status = "✅ PASS" if result == expected else "❌ FAIL"
        print(f"\nTest {i}: {status}")
        print(f"  Expected: {expected}")
        print(f"  Got:      {result}")

        if result != expected:
            print(f"  ⚠️  Your utils.py extract_efs_ref() needs updating!")

except ImportError:
    print("\n❌ Could not import utils.py")
    print("   Make sure utils.py is in the same directory")
except Exception as e:
    print(f"\n❌ Error: {e}")

print("\n" + "=" * 60)
print("If you see FAIL above, update extract_efs_ref() in utils.py")
print("Use the same regex pattern as yopmail_link_retriever.py:")
print("")
print("  r\"EFS Ref:?\\s*([A-Z0-9_]+)\"  # Alphanumeric")
print("  r\"EFS[- ]?(\\d{6})\"             # Numeric")
print("=" * 60)