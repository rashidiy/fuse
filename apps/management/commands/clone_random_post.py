from glob import glob
from random import choice

from django.core.management import BaseCommand
from faker import Faker

from apps.models import Post, Category

fake = Faker()


class Command(BaseCommand):
    help = 'Clone random Posts from exists Posts'

    def add_arguments(self, parser):
        parser.add_argument('total', type=int, help='Indicates the number of Posts to be created')

    def handle(self, *args, **kwargs):
        total = kwargs['total']
        images = glob("medias/post/*/*.png")
        print(images)
        if not images:
            raise 'Images Not Fount as "medias/post/*/*.png"'
        categories = Category.objects.all()
        if not categories:
            raise BaseException('Category count must be > 1')

        for i in range(total):
            category = choice(categories)
            post = Post.objects.create(
                title=f"{fake.name()} & {fake.name()}",
                image=choice(images)[7:],
                body=f"<p>{fake.text()}<br><br>{fake.text()}<br><br>{fake.text()}</p>",
                user_id=1,
                status='active',
            )
            post.category.add(category)
            post.save()