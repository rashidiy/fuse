from datetime import timedelta

from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth.models import AbstractUser
from django.db.models import TextField, JSONField, Model, ForeignKey, DateTimeField, CharField, SlugField, \
    CASCADE, RESTRICT, \
    BooleanField, IntegerField, ManyToManyField, SET_DEFAULT, EmailField, Manager
from django.utils.text import slugify
from django.utils.timezone import now
from django_resized import ResizedImageField


class ActivePostManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status='active')


class User(AbstractUser):
    phone = CharField(max_length=30, null=True)
    is_active = BooleanField(default=True)
    avatar = ResizedImageField(size=[800, 800], crop=['middle', 'center'], upload_to='users/images',
                               default='users/default.jpg')
    bio = TextField(null=True)
    social_accounts = JSONField(null=True)

    def save(self, *args, **kwargs):
        self.username = self.username.lower()
        return super(User, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Foydalanuvchi'  # noqa
        verbose_name_plural = 'Foydalanuvchilar'  # noqa


class Category(Model):
    name = CharField(max_length=225)
    image = ResizedImageField(size=[660, 170], crop=['middle', 'center'], upload_to='category/image')
    slug = SlugField()
    light = BooleanField(default=False)

    class Meta:
        verbose_name = 'Categoriya'  # noqa
        verbose_name_plural = 'Categoriyalar'  # noqa

    def __str__(self):
        return self.name

    @property
    def post_count(self):
        return self.post_set.filter(status='active').count()


class Post(Model):
    category = ManyToManyField(Category)
    title = CharField(max_length=100)
    slug = SlugField(max_length=255, unique=True)
    body = RichTextUploadingField()
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    user = ForeignKey(User, on_delete=RESTRICT)
    status = CharField(max_length=50, default='pending',
                       choices=[('active', 'ACTIVE'), ('pending', 'PENDING'), ('restrict', 'CANCEL')])
    image = ResizedImageField(size=[1500, 790], crop=['middle', 'center'], upload_to='post/%m')
    actives = ActivePostManager()
    objects = Manager()

    def slug_generator(self):
        slug = slugify(self.title)
        while Post.objects.filter(slug=slug).exists():
            slug = Post.objects.filter(slug=slug).first().slug
            if '-' in slug:
                try:
                    if slug.split('-')[-1] in self.title:
                        slug += '-1'
                    else:
                        slug = '-'.join(slug.split('-')[:-1]) + '-' + str(int(slug.split('-')[-1]) + 1)
                except:
                    slug = slug + '-1'
            else:
                slug += '-1'
        self.slug = slug

    def save(self, *args, **kwargs):
        self.slug_generator()
        super().save(*args, **kwargs)

    @property
    def comment_count(self):
        return self.comment_set.count()

    @property
    def views_count(self):
        return self.views_set.count()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Post'  # noqa
        verbose_name_plural = 'Postlar'  # noqa
        ordering = ('created_at',)


class Comment(Model):
    text = TextField()
    created_at = DateTimeField(auto_now=True)
    post = ForeignKey(Post, CASCADE)
    user = ForeignKey(User, RESTRICT, null=True)
    like_count = IntegerField(default=0)

    def __str__(self):
        return self.post.title

    class Meta:
        verbose_name = 'Comment'  # noqa
        verbose_name_plural = 'Commentlar'  # noqa


class Contact(Model):
    user = ForeignKey(User, RESTRICT)
    about = CharField(max_length=255)
    email = EmailField(max_length=255)
    message = CharField(max_length=2048)
    created_at = DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.about

    class Meta:
        verbose_name = 'Ariza'  # noqa
        verbose_name_plural = 'Arizalar'  # noqa


class Views(Model):
    post = ForeignKey(Post, CASCADE)
    user = ForeignKey(User, CASCADE)
    seen_at = DateTimeField(auto_now_add=True)
