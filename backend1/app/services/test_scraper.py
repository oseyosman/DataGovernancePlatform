"""
Test script for AnnualReports.com scraper
Author: Osman Yildiz

This script tests the web scraper functionality independently
"""
import sys
import os

# Add parent directories to path
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, backend_dir)

from backend1.app.services.scraper import AnnualReportsScraper
import json


def test_scrape_apple():
    """Test scraping Apple Inc."""
    print("=" * 80)
    print("Testing: Scrape Apple Inc.")
    print("=" * 80)
    
    scraper = AnnualReportsScraper(rate_limit_delay=0.5)
    company_data = scraper.scrape_company('apple-inc')
    
    if company_data:
        print("\n✅ Successfully scraped Apple Inc.")
        print(f"\nCompany Name: {company_data['name']}")
        print(f"Ticker: {company_data['ticker']}")
        print(f"Exchange: {company_data['exchange']}")
        print(f"Industry: {company_data['industry']}")
        print(f"Sector: {company_data['sector']}")
        print(f"Website: {company_data['website']}")
        print(f"\nDescription: {company_data['description'][:200]}...")
        print(f"\nAnnual Reports Found: {len(company_data['annual_reports'])}")
        
        if company_data['annual_reports']:
            print("\nRecent Reports:")
            for report in company_data['annual_reports'][:5]:
                print(f"  - {report['year']}: {report['title']}")
                if report['pdf_url']:
                    print(f"    PDF: {report['pdf_url']}")
                if report['view_url']:
                    print(f"    View: {report['view_url']}")
        
        # Save to file for inspection
        with open('apple_scraped_data.json', 'w', encoding='utf-8') as f:
            json.dump(company_data, f, indent=2)
        print("\n💾 Saved detailed data to: apple_scraped_data.json")
        
        return True
    else:
        print("\n❌ Failed to scrape Apple Inc.")
        return False


def test_search_google():
    """Test searching for Google"""
    print("\n" + "=" * 80)
    print("Testing: Search for 'Google'")
    print("=" * 80)
    
    scraper = AnnualReportsScraper(rate_limit_delay=0.5)
    results = scraper.search_companies('Google')
    
    if results:
        print(f"\n✅ Found {len(results)} companies")
        for i, company in enumerate(results[:5], 1):
            print(f"{i}. {company['name']} - {company['slug']}")
        return True
    else:
        print("\n❌ No results found")
        return False


def test_scrape_microsoft():
    """Test scraping Microsoft"""
    print("\n" + "=" * 80)
    print("Testing: Scrape Microsoft")
    print("=" * 80)
    
    scraper = AnnualReportsScraper(rate_limit_delay=0.5)
    company_data = scraper.scrape_company('microsoft-corp')
    
    if company_data:
        print(f"\n✅ Successfully scraped: {company_data['name']}")
        print(f"Ticker: {company_data['ticker']}")
        print(f"Reports Found: {len(company_data['annual_reports'])}")
        return True
    else:
        print("\n❌ Failed to scrape Microsoft")
        return False


def main():
    """Run all tests"""
    print("\n🚀 Starting AnnualReports.com Scraper Tests\n")
    
    tests = [
        ("Scrape Apple", test_scrape_apple),
        ("Search Google", test_search_google),
        ("Scrape Microsoft", test_scrape_microsoft),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == '__main__':
    exit(main())
