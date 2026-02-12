import requests
from bs4 import BeautifulSoup

def check_company(slug):
    url = f"https://www.annualreports.com/Company/{slug}"
    print(f"Checking URL: {url}")
    try:
        response = requests.get(url, allow_redirects=True)
        print(f"Status Code: {response.status_code}")
        print(f"Final URL: {response.url}")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        h1 = soup.find('h1')
        print(f"H1: {h1.get_text(strip=True) if h1 else 'None'}")
        
        # Check for search results
        if "Search" in response.url or "Companies?search" in response.url:
             print("Redirected to search/companies page.")

    except Exception as e:
        print(f"Error: {e}")

check_company('home-depot-inc')
check_company('the-home-depot-inc')
check_company('coca-cola-company')
check_company('the-coca-cola-company')
