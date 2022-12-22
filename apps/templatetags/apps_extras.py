from django import template
from django.core.handlers.wsgi import WSGIRequest
from django.utils.html import format_html
from rest_framework.reverse import reverse_lazy

register = template.Library()


@register.filter
def get_page_circle(request: WSGIRequest, page):
    """Check page is active """
    if request.method == "GET":
        site_page = request.GET.get('page', 1)
        other_methods = ''.join([f"&{i}={v}" for i, v in dict(request.GET).items() if i != 'page'])
        blog = reverse_lazy("blog")
        if page == site_page:
            circle = format_html('<li class="active">'
                                 f'<a href="{blog}?page={page}{other_methods}">{page}</a>'
                                 '</li>')
        else:
            circle = format_html('<li class="pagination__page-number">'
                                 f'<a href="{blog}?page={page}{other_methods}">{page}</a>'
                                 '</li>')
        return circle


@register.filter
def get_url_nth_path(request, n):
    path = request.path.split('/')
    while '' in path:
        path.remove('')
    return path[n]


@register.filter
def next_page(request: WSGIRequest):
    if request.GET:
        nxt_pg = request.GET.get('next')
        if nxt_pg:
            print([nxt_pg])
            return nxt_pg
    return ''
