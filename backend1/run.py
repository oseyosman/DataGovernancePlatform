"""
Data Governance & Compliance Platform
Main application entry point

Author: Osman Yildiz
Walsh College - MSIT Capstone Project
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend1.app import create_app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    print("=" * 60)
    print("Data Governance & Compliance Platform")
    print("=" * 60)
    print(f"API Server: http://localhost:{port}")
    print(f"Health Check: http://localhost:{port}/health")
    print(f"Auth Endpoint: http://localhost:{port}/api/auth/register")
    print(f"Login Endpoint: http://localhost:{port}/api/auth/login")
    print(f"Dashboard: http://localhost:{port}/api/dashboard/overview")
    print(f"Companies API: http://localhost:{port}/api/companies")
    print("=" * 60)
    print("\nServer is running... Press CTRL+C to stop\n")
    
    app.run(host='0.0.0.0', port=port, debug=True)