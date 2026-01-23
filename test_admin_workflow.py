import requests
import sys

BASE_URL = "http://localhost:5000/api"

def run_test():
    print("Starting Admin Workflow Test...")

    # 1. Login as User to create report
    print("Logging in as regular user...")
    res = requests.post(f"{BASE_URL}/auth/login", json={"username": "user", "password": "user123"})
    print(f"Login Response: {res.status_code} {res.text}")
    if res.status_code != 200:
        print("Failed to login as user")
        sys.exit(1)
    try:
        user_token = res.json()['access_token']
    except KeyError:
        print(f"Token missing in response: {res.json()}")
        sys.exit(1)
    
    # 2. Create Report
    print("Creating draft report...")
    res = requests.post(
        f"{BASE_URL}/reports/", 
        headers={"Authorization": f"Bearer {user_token}"},
        data={"title": "Auto Test Doc", "report_type": "Policy", "description": "Testing workflow"}
    )
    if res.status_code != 201:
        print(f"Failed to create report: {res.text}")
        sys.exit(1)
    report_id = res.json()['report']['id']
    print(f"Report created with ID: {report_id}")

    # 3. Submit Report (User)
    print("Submitting report...")
    res = requests.put(
        f"{BASE_URL}/reports/{report_id}",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"status": "submitted"}
    )
    if res.status_code != 200:
        print(f"Failed to submit report: {res.text}")
        sys.exit(1)
    print("Report submitted.")

    # 4. Login as Admin
    print("Logging in as Admin...")
    res = requests.post(f"{BASE_URL}/auth/login", json={"username": "admin", "password": "admin123"})
    if res.status_code != 200:
        print(f"Failed to login as admin: {res.text}")
        sys.exit(1)
    admin_token = res.json()['access_token']

    # 5. Fetch Report (Admin)
    print("Fetching report as admin...")
    res = requests.get(
        f"{BASE_URL}/reports/{report_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    if res.status_code != 200:
        print(f"Failed to fetch report: {res.text}")
        sys.exit(1)
    
    # 6. Approve Report (Admin)
    print("Approving report...")
    res = requests.put(
        f"{BASE_URL}/reports/{report_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "approved"}
    )
    if res.status_code != 200:
        print(f"Failed to approve report: {res.text}")
        sys.exit(1)
    
    status = res.json()['report']['status']
    if status == 'approved':
        print("SUCCESS: Report was approved by admin.")
    else:
        print(f"FAILURE: Report status is {status}")

if __name__ == "__main__":
    try:
        run_test()
    except Exception as e:
        print(f"An error occurred: {e}")
