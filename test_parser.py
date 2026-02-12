from backend1.app.services.parser import parser

# Test with a known PDF URL (e.g., Apple 10-K or similar if accessible, or just a dummy one)
# Since I can't guarantee external access to a specific 10-K without searching, 
# I'll rely on the parser to handle errors gracefully if URL is bad.
# But I can try to test the find_keywords logic with text.

text = """
This is a sample text from an Annual Report.
We are fully committed to ISO 27001 certification.
The company has implemented a Clawback Policy for executive compensation.
"""

keywords = parser.find_keywords(text)
print(f"Text Analysis Results: {keywords}")

# Test keyword extraction
assert keywords.get('ISO 27001') == True
assert keywords.get('Clawback Policy') == True
assert keywords.get('GDPR') == False

print("Parser Keyword Logic verified.")
