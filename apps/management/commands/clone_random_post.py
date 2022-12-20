import os
from glob import glob
from random import choice

from django_resized import ResizedImageField
from faker import Faker
from django.core.management import BaseCommand

from apps.models import Post, Category

fake = Faker()


class Command(BaseCommand):
    help = 'Clone random Posts from exists Posts'

    def add_arguments(self, parser):
        parser.add_argument('total', type=int, help='Indicates the number of Posts to be created')

    def handle(self, *args, **kwargs):
        total = kwargs['total']
        images = glob("medias/post/*/*.png")
        if not images:
            raise 'Images Not Fount as "medias/post/*/*.png"'
        categories = Category.objects.all()
        if not categories:
            raise BaseException('Category count must be > 1')

        for i in range(total):
            category = choice(categories)
            post = Post.objects.create(
                title=fake.name(),
                image=ResizedImageField(),
                body=f"<p>{fake.text()}</p>",
                user_id=1,
                status='active',
            )
            post.category.add(category)
            post.save()



