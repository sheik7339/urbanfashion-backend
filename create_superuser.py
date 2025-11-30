import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'urbanfashion.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Delete existing admin user if exists
try:
    admin = User.objects.get(username='admin')
    admin.delete()
    print("Deleted existing admin user")
except User.DoesNotExist:
    print("No existing admin user found")

# Create new superuser with password
admin = User.objects.create_superuser(
    username='admin',
    email='admin@urbanfashion.com',
    password='admin123'
)

print("\n" + "="*50)
print("SUPERUSER CREATED SUCCESSFULLY!")
print("="*50)
print("Username: admin")
print("Email: admin@urbanfashion.com")
print("Password: admin123")
print("="*50)
print("\nYou can now login to:")
print("http://localhost:8000/admin/")
print("="*50)
