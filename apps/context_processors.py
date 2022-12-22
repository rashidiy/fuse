from datetime import timedelta

from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Count
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_encode
from django.utils.timezone import now

from apps.models import Category, Post, Views


def context_category(request: WSGIRequest):
    return {
        'categories': Category.objects.all(),
        'location': 'Uzbekistan, Tashkent',
        'phone_number': '+998(33)077-17-12',
        'email': 'bubbless7456@gmail.com',
        'description': "Bemorni davolash juda muhim, bemorni bemor kuzatib boradi, lekin ayni paytda ba'zi "
                       "katta og'riqlar bilan. Kim batareyaning batareyasini yoki oson bo'lganlarni to'xtatib qo'ydi.",
        'feature_posts': Post.actives.filter(user__is_superuser=True)[:3]
    }


def context_trending_post(request):
    last = now() - timedelta(30)
    posts_id = Views.objects.filter(seen_at__gt=last).values_list('post').annotate(
        count=Count('post')).order_by('-count')[:5]
    return {
        'trending_posts': [Post.objects.get(pk=pk) for pk, count in posts_id]
    }
