"""
Simple test script for the scraper - run from project root
"""
import sys
sys.path.insert(0, '.')

from backend1.app.services.scraper import AnnualReportsScraper
import json


def main():
    print("=" * 80)
    print("Testing AnnualReports.com Scraper")
    print("=" * 80)
    
    scraper = AnnualReportsScraper(rate_limit_delay=0.5)
    
    # Test 1: Scrape Apple
    print("\n[1/3] Scraping Apple Inc...")
    apple_data = scraper.scrape_company('apple-inc')
    
    if apple_data:
        print("[SUCCESS]")
        print(f"   Company: {apple_data['name']}")
        print(f"   Ticker: {apple_data['ticker']}")
        print(f"   Exchange: {apple_data['exchange']}")
        print(f"   Industry: {apple_data['industry']}")
        print(f"   Reports Found: {len(apple_data['annual_reports'])}")
        
        if apple_data['annual_reports']:
            print(f"\n   Recent Reports:")
            for report in apple_data['annual_reports'][:3]:
                print(f"     - {report['year']}: {report['title']}")
        
        # Save detailed data
        with open('apple_scraped_data.json', 'w', encoding='utf-8') as f:
            json.dump(apple_data, f, indent=2)
        print(f"\n   Saved to: apple_scraped_data.json")
    else:
        print("[FAILED] to scrape Apple")
        return False
    
    # Test 2: Search for Microsoft
    print("\n[2/3] Searching for 'Microsoft'...")
    search_results = scraper.search_companies('Microsoft')
    
    if search_results:
        print(f"[SUCCESS] Found {len(search_results)} results")
        for i, company in enumerate(search_results[:3], 1):
            print(f"   {i}. {company['name']} - {company['slug']}")
    else:
        print("[FAILED] Search returned no results")
    
    # Test 3: Scrape Microsoft
    print("\n[3/3] Scraping Microsoft...")
    ms_data = scraper.scrape_company('microsoft-corp')
    
    if ms_data:
        print("[SUCCESS]")
        print(f"   Company: {ms_data['name']}")
        print(f"   Ticker: {ms_data['ticker']}")
        print(f"   Reports Found: {len(ms_data['annual_reports'])}")
    else:
        print("[FAILED] to scrape Microsoft")
    
    print("\n" + "=" * 80)
    print("Scraper test complete!")
    print("=" * 80)
    return True


if __name__ == '__main__':
    try:
        success = main()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n[ERROR]: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
