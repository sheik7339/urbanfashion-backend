from django.contrib.auth import get_user_model

User = get_user_model()
admin = User.objects.get(username='admin')
admin.set_password('admin123')  # Change this to your preferred password
admin.save()
print("Password set successfully!")
