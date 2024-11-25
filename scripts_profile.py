from django.contrib.auth.models import User
from gestion.models import UserProfile

users = User.objects.all()

for user in users:
    if not hasattr(user, 'profile'):
        UserProfile.objects.create(user=user)
