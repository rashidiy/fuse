from django import template
from django.core.handlers.wsgi import WSGIRequest

register = template.Library()


@register.filter
def is_page(request: WSGIRequest, page):
    """Check page is active """
    if request.method == "GET":
        site_page = int(request.GET.get('page') or 1)
        return site_page == page
    return False


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
