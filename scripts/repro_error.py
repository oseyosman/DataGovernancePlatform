import requests
import json

BASE_URL = "http://localhost:5000"

def login(username, password):
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "username": username,
        "password": password
    })
    return response.json().get("access_token")

def create_report(token):
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "title": "Test Report",
        "report_type": "Annual Report"
    }
    response = requests.post(f"{BASE_URL}/api/reports/", headers=headers, json=data)
    return response.json().get("report", {}).get("id")

def update_report_trigger_error(token, report_id):
    headers = {"Authorization": f"Bearer {token}"}
    # This update payload does NOT rely on 'approved' status, or relies on it partially
    # purely updating description should trigger it if warning_message is used unconditionally
    data = {
        "description": "Updated description"
    }
    print(f"Updating report {report_id} with data: {data}")
    response = requests.put(f"{BASE_URL}/api/reports/{report_id}", headers=headers, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

def main():
    token = login("admin", "admin123")
    if not token:
        print("Login failed")
        return

    report_id = create_report(token)
    if not report_id:
        print("Failed to create report")
        return
    
    print(f"Created report {report_id}")
    update_report_trigger_error(token, report_id)

if __name__ == "__main__":
    main()
