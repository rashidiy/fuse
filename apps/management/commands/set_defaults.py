import os
from glob import glob
from random import choice, randint

from django.core.management import BaseCommand
from faker import Faker

from apps.models import Post, Category, User

fake = Faker()


class Command(BaseCommand):
    help = 'Set Default items for work website'
    os.chdir('medias/')

    def handle(self, *args, **kwargs):
        images = glob("post/*/*.png")

        if not images:
            raise 'Images Not Fount as "fuse/medias/post/*/*.png"'
        category = Category.objects.create(
            name='Default',
            image='category/image/default.png',
            slug='default'
        )
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            raise BaseException('You must be a create superuser following this command: ./manage.py createsuperuser')
        for image in images:
            post = Post.objects.create(
                title=f"{fake.name()} & {fake.name()}",
                image=image,
                body=f"<p>{fake.text()}<br><br>{fake.text()}<br><br>{fake.text()}</p>",
                user_id=user.pk,
                status='active',
            )
            post.category.add(category)
            post.save()
