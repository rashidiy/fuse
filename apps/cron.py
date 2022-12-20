import os

from apps.models import User, Post, Category

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'root.settings')



def delete_expired_users():
    Category.objects.create()
