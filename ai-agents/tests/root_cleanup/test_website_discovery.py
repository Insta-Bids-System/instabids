"""
Test the website discovery logic directly
"""
import re

def test_website_discovery():
    """Test website discovery for Turf Grass Artificial Solutions"""
    
    business_name = "Turf Grass Artificial Solutions"
    
    # This is the logic from research_based_agent.py lines 147-151
    name_clean = re.sub(r"[^a-zA-Z0-9\s]", "", business_name).replace(" ", "").lower()
    potential_sites = [
        f"https://{name_clean}.com",
        f"https://www.{name_clean}.com",
    ]
    
    print(f"Business name: {business_name}")
    print(f"Cleaned name: {name_clean}")
    print(f"Potential websites:")
    for site in potential_sites:
        print(f"  - {site}")
    
    # Expected result: https://turfgrassartificialsolutions.com
    expected = "https://turfgrassartificialsolutions.com"
    if expected in potential_sites:
        print(f"\n✅ SUCCESS: Found expected website {expected}")
    else:
        print(f"\n❌ FAIL: Expected {expected} not in potential sites")

if __name__ == "__main__":
    test_website_discovery()