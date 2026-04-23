#!/usr/bin/env python
"""
Script to create admin user in Django
Uses the custom User model from userauth app
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dms.settings')
django.setup()

from userauth.models import User

# Check existing users
print("\n" + "="*60)
print("CHECKING EXISTING USERS")
print("="*60)
users = User.objects.all()
print(f"Total users in database: {users.count()}")

if users.count() > 0:
    print("\nExisting users:")
    for user in users:
        print(f"  ✓ Username: {user.email}")
        print(f"    Email: {user.email}")
        print(f"    Is Superuser: {user.is_superuser}")
        print(f"    Is Staff: {user.is_staff}")
        print(f"    Is Active: {user.is_active}")
        print()
else:
    print("\n❌ No users found. Creating admin user...")
    try:
        # Create superuser with all required flags
        admin_user = User.objects.create_superuser(email='admin@example.com', password='admin123')
        # Explicitly set required flags for custom User model
        admin_user.is_active = True
        admin_user.is_staff = True
        admin_user.is_superadmin = True
        admin_user.is_admin = True
        admin_user.first_name = 'Admin'
        admin_user.last_name = 'User'
        admin_user.username = 'admin'
        admin_user.save()
        
        print("\n" + "="*60)
        print("✅ ADMIN USER CREATED SUCCESSFULLY!")
        print("="*60)
        print(f"Email: {admin_user.email}")
        print(f"Is Superuser: {admin_user.is_superuser}")
        print(f"Is Staff: {admin_user.is_staff}")
        print(f"Is Active: {admin_user.is_active}")
        print("\nYou can now login at:")
        print("URL: http://127.0.0.1:8000/projectName/admin/")
        print("Email: admin@example.com")
        print("Password: admin123")
        print("="*60 + "\n")
    except Exception as e:
        print(f"\n❌ Error creating user: {e}\n")
        import traceback
        traceback.print_exc()
