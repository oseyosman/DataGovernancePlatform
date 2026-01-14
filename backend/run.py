"""
Data Governance & Compliance Platform
Main application entry point

Author: Osman Yildiz
Walsh College - MSIT Capstone Project
"""
from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    print("=" * 60)
    print("🚀 Data Governance & Compliance Platform")
    print("=" * 60)
    print(f"📍 API Server: http://localhost:{port}")
    print(f"💚 Health Check: http://localhost:{port}/health")
    print(f"🔐 Auth Endpoint: http://localhost:{port}/api/auth/login")
    print(f"📊 Dashboard: http://localhost:{port}/api/dashboard/overview")
    print("=" * 60)
    print("\n✅ Server is running... Press CTRL+C to stop\n")
    
    app.run(host='0.0.0.0', port=port, debug=True)