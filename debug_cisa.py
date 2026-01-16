import urllib.request
import xml.etree.ElementTree as ET

# The URL we are currently using
URL = "https://www.cisa.gov/sites/default/files/api_v1/cybersecurity_advisories.xml"
# The Alternative (Standard RSS) URL
ALT_URL = "https://www.cisa.gov/cybersecurity-advisories/all.xml"

def test_feed(url):
    print(f"\n--- TESTING: {url} ---")
    try:
        req = urllib.request.Request(
            url, 
            data=None, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            data = response.read()
            print(f"Status: {response.getcode()}")
            print(f"Data Length: {len(data)} bytes")
            
            try:
                root = ET.fromstring(data)
                # Check for standard RSS structure
                items = root.findall('./channel/item')
                print(f"RSS Items found (channel/item): {len(items)}")
                
                if len(items) == 0:
                    # Check for Atom structure (ns)
                    print("Checking for Atom/Other structure...")
                    # Print first 100 chars to see what we got
                    print(f"Snippet: {data[:200]}")
            except Exception as e:
                print(f"XML PARSE ERROR: {e}")
                
    except Exception as e:
        print(f"CONNECTION ERROR: {e}")

test_feed(URL)
test_feed(ALT_URL)
