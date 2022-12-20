from random import choice

from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse, path, URLPattern
from django.utils.html import format_html

from apps.models import User, Category, Comment, Post, Contact
from apps.tasks import send_text_to_mail


@admin.register(User)
class UserAdmin(ModelAdmin):
    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
        'is_active',
        'date_joined',
        'bio',
        'avatar',
        'social_accounts'
    )
    exclude = (
        'is_staff',
        'is_active',
        'is_superuser',
        'date_joined',
        'last_login',
        'groups',
        'user_permissions'
    )


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ('name', 'ctg_image')

    @staticmethod
    def ctg_image(obj: Post):
        return format_html(f'<img style="border-radius: 15px" src="{obj.image.url}">')


@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    list_display = ('text',)
    readonly_fields = ('like_count',)


@admin.register(Post)
class PostAdmin(ModelAdmin):
    list_display = ('title', 'created_at', 'categories', 'status_icons', 'buttons', 'preview')
    exclude = ('slug', 'status')
    search_fields = ('title',)
    list_filter = ('status', 'category')

    def get_urls(self):
        urls = super().get_urls()
        urls += [
            path('accept/<int:post>', self.accept_url),
            path('cancel/<int:post>', self.cancel_url),
            path('preview/<int:pk>', self.preview_url)
        ]
        return urls

    def preview(self, obj):
        return format_html(f'<a href="preview/{obj.pk}">'
                           '<input type="button" value="ViewPost" class="view" style="'
                           'background-color: lightBlue;'
                           'margin: 0 .1rem;'
                           'border-radius: 1.2rem;'
                           'letter-spacing: .8px;'
                           'font-weight: bold;">'
                           '</a>')

    def preview_url(self, request, pk):
        post = Post.objects.filter(pk=pk).first()
        data = {
            'post': post,
            'helper_buttons': f'<div class="col-12 col-sm-4 ml-3"><a class="btn -normal" href="/admin/apps/post/accept/{pk}">Accept</a></div>'
                              f'<div class="col-12 col-sm-4 ml-3"><a class="btn -normal" href="/admin/apps/post/cancel/{pk}">Cancel</a></div>'

        }
        posts = list(post.category.first().post_set.all())
        posts.remove(data.get('post'))
        data['related_posts'] = [choice(posts)]
        while len(set(data['related_posts'])) != 2:
            data['related_posts'] += [choice(posts)]
        return render(request, 'apps/post.html', data)

    def accept_url(self, request, post):
        post = Post.objects.filter(pk=post).first()
        post.status = 'active'
        post.save()
        return redirect("/admin/apps/post/")

    def cancel_url(self, request, post):
        post = Post.objects.filter(pk=post).first()
        post.status = 'restrict'
        post.save()
        return redirect("/admin/apps/post/")

    def categories(self, obj):
        links = [
            f'<a style="font-weight: bold;" href="{reverse("admin:apps_category_change", args=(c.id,))}">{c.name}</a>'
            for c in obj.category.all()]
        return format_html(", ".join(links))

    def buttons(self, obj):
        if obj.status == 'pending':
            val = f'<a href="accept/{obj.pk}">' \
                  '<input type="button" value="Accept" class="accept" style="' \
                  'background-color: limegreen;' \
                  'margin: 0 .1rem;' \
                  'border-radius: 1.2rem;' \
                  'letter-spacing: .8px;' \
                  'font-weight: bold;">' \
                  '</a>' \
                  f'<a href="cancel/{obj.pk}">' \
                  '<input type="button" value="Restrict" class="cancel" style="' \
                  'background-color: red;' \
                  'margin: 0 .1rem;' \
                  'border-radius: 1.2rem;' \
                  'letter-spacing: .8px;' \
                  'font-weight: bold;">' \
                  '</a>'
        else:
            if obj.status == 'active':
                val = f'<p style="' \
                      f'text-transform: uppercase;' \
                      f'color: limegreen;' \
                      f'font-weight: bold;' \
                      f'font-size: 15px;' \
                      f'">Accepted</p>'
            else:
                val = f'<p style="' \
                      f'text-transform: uppercase;' \
                      f'color: red;' \
                      f'font-weight: bold;' \
                      f'font-size: 15px;' \
                      f'">Rejected</p>'
        return format_html(val)

    def status_icons(self, obj):
        center = (lambda x: f'<div style="padding-left: 13%">{x}</div>')
        action = {
            'active': center(
                '<svg width="20px" xmlns="http://www.w3.org/2000/svg" style="fi'
                'll: green" viewBox="0 0 512 512"><path d="M470.6 105.4c12.5 12'
                '.5 12.5 32.8 0 45.3l-256 256c-12.5 12.5-32.8 12.5-45.3 0l-128-'
                '128c-12.5-12.5-12.5-32.8 0-45.3s32.8-12.5 45.3 0L192 338.7 425'
                '.4 105.4c12.5-12.5 32.8-12.5 45.3 0z"/></svg>'),
            'restrict': center(
                '<svg width="20px" xmlns="http://www.w3.org/2000/svg" style="fill: red" viewBox="0 0 512 512'
                '"><path d="M256 512c141.4 0 256-114.6 256-256S397.4 0 256 0S'
                '0 114.6 0 256S114.6 512 256 512zM175 175c9.4-9.4 24.6-9.4 33'
                '.9 0l47 47 47-47c9.4-9.4 24.6-9.4 33.9 0s9.4 24.6 0 33.9l-47'
                ' 47 47 47c9.4 9.4 9.4 24.6 0 33.9s-24.6 9.4-33.9 0l-47-47-47'
                ' 47c-9.4 9.4-24.6 9.4-33.9 0s-9.4-24.6 0-33.9l47-47-47-47c-9'
                '.4-9.4-9.4-24.6 0-33.9z"/></svg>'),
            'pending': center(
                '<svg width="20px" xmlns="http://www.w3.org/2000/svg" style="fill: gray" viewBox="0 0 512 512"'
                '><path d="M232 120C232 106.7 242.7 96 256 96C269.3 96 280 106'
                '.7 280 120V243.2L365.3 300C376.3 307.4 379.3 322.3 371.1 333.'
                '3C364.6 344.3 349.7 347.3 338.7 339.1L242.7 275.1C236 271.5 2'
                '32 264 232 255.1L232 120zM256 0C397.4 0 512 114.6 512 256C512'
                ' 397.4 397.4 512 256 512C114.6 512 0 397.4 0 256C0 114.6 114.'
                '6 0 256 0zM48 256C48 370.9 141.1 464 256 464C370.9 464 464 37'
                '0.9 464 256C464 141.1 370.9 48 256 48C141.1 48 48 141.1 48 25'
                '6z"/></svg>')
        }
        return format_html(action[obj.status])

    status_icons.short_description = 'STATUS'


@admin.register(Contact)
class ContactAdmin(ModelAdmin):
    list_display = 'user', 'about', 'created_at'
    readonly_fields = 'user', 'about', 'email', 'created_at', 'message'
    change_form_template = 'admin/custom/change_form.html'''
    ordering = ('-created_at',)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        if request.method == 'POST':
            message = request.POST.get('message')
            if message:
                contact = Contact.objects.get(pk=object_id)
                messages.add_message(request, messages.INFO, '')
                send_text_to_mail.delay(contact.email, message, 'Fuse | Answer for your Feedback', 'html')
        return super().change_view(request, object_id, form_url, extra_context)