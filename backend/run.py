#!/usr/bin/env python3
"""
StackIt Flask Application Runner
Simple script to run the Flask backend
"""

import os
from dotenv import load_dotenv
from app import create_app
from models import db, User

# Load environment variables
load_dotenv()

# Create Flask app
app = create_app()

if __name__ == '__main__':
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        # Create default admin if it doesn't exist
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@stackit.com',
                role='admin',
                avatar='⚡'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("✅ Created default admin user: admin/admin123")
    
    print("🚀 Starting StackIt Backend...")
    print("📍 API will be available at: http://localhost:5000")
    print("📚 API Documentation endpoints:")
    print("   Health Check: GET /api/health")
    print("   Auth: POST /api/auth/login, /api/auth/register")
    print("   Questions: GET /api/questions")
    print("   Tags: GET /api/tags")
    print("\n💡 Default admin credentials: admin / admin123")
    print("🔧 Make sure your React frontend is configured to use http://localhost:5000\n")
    
    # Run the app
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        threaded=True
    )