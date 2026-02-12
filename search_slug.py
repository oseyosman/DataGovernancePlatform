import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend1.app.services.scraper import search_companies

queries = [
    'Nvidia',
    'Amazon', 
    'Advanced Micro Devices',
    'Costco',
    'Home Depot',
    'Coca Cola' 
]

print("Verifying slugs...")
for q in queries:
    print(f"\nSearching for '{q}':")
    results = search_companies(q)
    if results:
        company = results[0]
        print(f"  FOUND: {company['name']} -> {company['slug']}")
    else:
        print(f"  NOT FOUND: {q}")
