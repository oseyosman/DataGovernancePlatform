import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend1.app.services.scraper import search_companies

queries = [
    'Nvidia',
    'Microsoft',
    'Amazon',
    'Costco',
    'Home Depot',
    'Coca Cola',
    'AMD',
    'Intel',
    'Qualcomm',
    'Broadcom'
]

print("Verifying slugs...")
for q in queries:
    print(f"\nSearching for '{q}':")
    results = search_companies(q)
    for company in results[:3]:  # Show top 3 matches
        print(f"  - Name: {company['name']}, Slug: {company['slug']}")
