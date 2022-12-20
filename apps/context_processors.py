from django.core.handlers.wsgi import WSGIRequest
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_encode

from apps.models import Category, Post


def context_category(request: WSGIRequest):
    return {
        'categories': Category.objects.all(),
        'location': 'Uzbekistan, Tashkent',
        'phone_number': '+998(33)077-17-12',
        'email': 'bubbless7456@gmail.com',
        'description': "Bemorni davolash juda muhim, bemorni bemor kuzatib boradi, lekin ayni paytda ba'zi "
                       "katta og'riqlar bilan. Kim batareyaning batareyasini yoki oson bo'lganlarni to'xtatib qo'ydi.",
        'feature_posts': Post.objects.filter(user__is_superuser=True)[:3]
    }
