import requests
import json
import sys

BASE_URL = "http://localhost:5000/api"

def check_api():
    print("Logging in...")
    try:
        resp = requests.post(f"{BASE_URL}/auth/login", json={"username": "admin", "password": "admin123"})
        if resp.status_code != 200:
            print(f"Login failed: {resp.status_code} {resp.text}")
            return
        
        token = resp.json().get('token')
        print("Login successful. Token obtained.")
        
        print("Checking /companies/compliance-overview...")
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(f"{BASE_URL}/companies/compliance-overview", headers=headers)
        
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print("Success!")
            print(f"Total Companies: {data.get('total_companies')}")
            # Print average of first company to see if it varies
            if data.get('companies'):
                print(f"First Company Avg: {data['companies'][0].get('average_compliance')}")
        else:
            print(f"Error: {resp.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    check_api()
