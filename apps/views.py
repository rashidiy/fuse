from random import choice

from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetConfirmView
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.encoding import force_str, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, CreateView, FormView, UpdateView

from .forms import RegisterForm, PostQueueForm, SearchBoxForm, ContactForm, LoginPageForm, ForgetPasswordForm, \
    CommentForm
from .make_pdf import render_to_pdf
from .models import Category, Post, User, Views
from .tasks import send_text_to_mail
from .tokens import activation_token


class RegisterPageView(CreateView):
    form_class = RegisterForm
    template_name = 'apps/auth/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        form.instance.is_active = False
        email = form.instance.email
        user = form.save()
        token = activation_token.make_token(user)
        host = self.request.get_host()
        hashed_id = urlsafe_base64_encode(force_bytes(user.pk))
        activate_link = f'{host}/activate_account/{hashed_id}/{token}'
        send_text_to_mail.delay(email, activate_link, 'Fuse - Activate your Account', 'html')
        return super().form_valid(form)

    def form_invalid(self, form):
        return super(RegisterPageView, self).form_invalid(form)


class LoginPageView(LoginView):
    form_class = LoginPageForm
    template_name = 'apps/auth/login.html'


class ActivateAccountView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            login(request, user)
            return redirect('index')
        # else:
        #     invalid link
        # return render(request, 'registration/invalid.html')


class ResetPasswordView(PasswordResetConfirmView):
    template_name = 'apps/auth/reset_password.html'
    token_generator = activation_token

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)


class IndexView(ListView):
    template_name = 'apps/index.html'
    queryset = Category.objects.all()
    context_object_name = 'categories'

    def get_context_data(self, *, object_list=None, **kwargs):
        data = super().get_context_data(object_list=object_list, **kwargs)
        data['last_post'] = Post.actives.order_by('-created_at').first()
        data['posts'] = Post.actives.order_by('-created_at')[:4]
        data['all_posts'] = Post.actives.order_by('-created_at')
        data['all_posts'] = Post.actives.order_by('-created_at')
        return data


class AboutView(ListView):
    template_name = 'apps/about.html'
    model = Category


class BlogView(ListView):
    template_name = 'apps/blog-category.html'
    queryset = Post.actives

    def get_context_data(self, *, object_list=None, **kwargs):
        data = super().get_context_data(object_list=object_list, **kwargs)
        request = self.request
        if request.method == 'GET':
            if request.GET:
                filter_ = request.GET.get('filter')
                if filter_:
                    posts = Post.actives.order_by('-created_at').filter(status='active', title__icontains=filter_)
                else:
                    posts = Post.actives.order_by('-created_at').filter(
                        status='active',
                        category__slug=request.GET.get('category'))
            else:
                posts = Post.actives.order_by('-created_at')[:6]
            data['category'] = Category.objects.filter(slug=self.request.GET.get('category')).first() or None
            p = (int(request.GET.get('page', 1) or 1) - 1) * 6
            data['category_posts'] = posts[p:p + 6]
            data['posts_count'] = [i + 1 for i in range(len(posts) // 6 + 1)]
        return data


class ContactView(LoginRequiredMixin, CreateView):
    template_name = 'apps/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('contact')
    context_object_name = 's_uer'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class PostView(DetailView):
    template_name = 'apps/post.html'
    queryset = Post.actives
    model = Post
    context_object_name = 'post'

    def get(self, request, slug, *args, **kwargs):
        if not request.user.is_anonymous:
            post = Post.actives.get(slug=slug)
            Views.objects.create(
                user=request.user,
                post=post
            )
        return super().get(request, *args, **kwargs)

    def get_object(self, queryset=None):
        slug = self.kwargs.get('slug')
        return get_object_or_404(Post, slug=slug)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        posts = list(Post.actives.filter(status='active',
                                         slug=self.request.path.split('/')[-1]).first().category.first().post_set.all())
        posts.remove(data.get('post'))
        data['related_posts'] = [choice(posts)]
        while len(set(data['related_posts'])) != 2:
            data['related_posts'] += [choice(posts)]
        data['site_uri'] = f"http://{self.request.get_host()}{self.request.path}"
        return data


class CommentView(CreateView):
    form_class = CommentForm

    def get_success_url(self):
        if self.request.method == 'POST':
            post = Post.objects.get(pk=self.request.POST.get('post'))
            return reverse_lazy('post', kwargs={'slug': post.slug})
        return super().get_success_url()

    def get(self, request, *args, **kwargs):
        return redirect('index')


class DashboardListView(LoginRequiredMixin, CreateView):
    success_url = reverse_lazy('create_post')
    template_name = 'apps/dashboard.html'
    model = Category
    queryset = Category.objects.all()
    context_object_name = 'categories'
    form_class = PostQueueForm

    def form_valid(self, form):
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


class Http404notFound(TemplateView):
    template_name = 'apps/404-not-found.html'
    response_class = 404


class SearchBoxView(FormView):
    form_class = SearchBoxForm
    success_url = reverse_lazy('search_box')

    def get(self, request, *args, **kwargs):
        return redirect('index')

    def post(self, request: WSGIRequest, *args, **kwargs):
        if request.method == 'POST':
            like = request.POST.get('like')
            host = request.get_host()
            posts = [
                {
                    'title': post.title,
                    'url': f'/post/{post.slug}',
                    'image': post.image.url
                }
                for post in Post.actives.filter(title__icontains=like)
            ]
            return JsonResponse({
                'success': bool(like),
                'posts': posts
            })
        return redirect('index')


class UserUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'apps/profile.html'
    model = User
    fields = ('avatar', 'first_name', 'last_name', 'username', 'phone', 'email', 'bio')
    context_object_name = 's_user'
    success_url = reverse_lazy('profile', kwargs={'username': 'me'})

    def get_object(self, queryset=None):
        username = self.kwargs.get('username')
        if username == 'me':
            return get_object_or_404(User, pk=self.request.user.pk)
        return get_object_or_404(User, username=username)


class UserPasswordChangeView(PasswordChangeView):
    success_url = reverse_lazy('profile', kwargs={'username': 'me'})
    template_name = 'apps/profile.html'

    def get_object(self, queryset=None):
        username = self.kwargs.get('username')
        if username == 'me':
            return get_object_or_404(User, pk=self.request.user.pk)
        return get_object_or_404(User, username=username)


class ForgetPassword(FormView):
    template_name = 'apps/auth/forgot_password.html'
    form_class = ForgetPasswordForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        email = form.clean_email()
        host = self.request.get_host()
        user = User.objects.filter(email=email).first()
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = activation_token.make_token(user)
        activate_link = f'{host}/reset_password/{uid}/{token}'
        send_text_to_mail.delay(email, activate_link, 'Fuse | Reset Password', 'html')
        return super().form_valid(form)


class PdfGenerateView(DetailView):
    def get(self, request, *args, **kwargs):
        post = Post.objects.get(pk=kwargs.get('pk'))
        data = {
            'post': post,
        }
        pdf = render_to_pdf('apps/post_pdf.html', data)
        return HttpResponse(pdf, content_type='application/pdf')
