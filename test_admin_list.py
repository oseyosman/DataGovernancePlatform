import requests
import sys
import json

BASE_URL = "http://localhost:5000/api"

def run_test():
    print("Starting Admin List Test...")

    # 1. Login as Admin
    print("Logging in as Admin...")
    res = requests.post(f"{BASE_URL}/auth/login", json={"username": "admin", "password": "admin123"})
    if res.status_code != 200:
        print(f"Failed to login as admin: {res.text}")
        sys.exit(1)
    
    try:
        admin_token = res.json()['access_token']
        print("Admin login successful.")
    except KeyError:
        print(f"Token missing: {res.json()}")
        sys.exit(1)

    # 2. Fetch Reports
    print("Fetching reports...")
    res = requests.get(
        f"{BASE_URL}/reports/",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    if res.status_code != 200:
        print(f"Failed to fetch reports: {res.text}")
        sys.exit(1)
    
    data = res.json()
    print(f"Total Reports: {data.get('total', 0)}")
    
    reports = data.get('reports', [])
    submitted_docs = [r for r in reports if r['status'] in ['submitted', 'reviewed', 'approved']]
    
    print("\n--- Submitted Documents (Admin View) ---")
    if not submitted_docs:
        print("NO SUBMITTED DOCUMENTS FOUND.")
    else:
        for r in submitted_docs:
            print(f"ID: {r.get('id')} | Title: {r.get('title')} | Status: {r.get('status')} | CreatedBy: {r.get('created_by')}")
            
    print("\n--- Raw JSON Dump (First 3 reports) ---")
    print(json.dumps(reports[:3], indent=2))

if __name__ == "__main__":
    run_test()
