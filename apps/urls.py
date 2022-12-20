from django.contrib.auth.views import LogoutView
from django.urls import path, reverse_lazy

from .views import (IndexView, BlogView, AboutView, ActivateAccountView,
                    ContactView, PostView, RegisterPageView, LoginPageView, DashboardListView,
                    SearchBoxView, UserUpdateView, UserPasswordChangeView, ForgetPassword, ResetPasswordView)

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('blog', BlogView.as_view(), name='blog'),
    path('about', AboutView.as_view(), name='about'),
    path('login/', LoginPageView.as_view(), name='login'),
    path('contact', ContactView.as_view(), name='contact'),
    path('post/<str:slug>', PostView.as_view(), name='post'),
    path('search', SearchBoxView.as_view(), name='search_box'),
    path('register', RegisterPageView.as_view(), name='register'),
    path('create_post', DashboardListView.as_view(), name='create_post'),
    path('forget_password', ForgetPassword.as_view(), name='forget_password'),
    path('profile/<str:username>', UserUpdateView.as_view(), name='profile'),
    path('change_password', UserPasswordChangeView.as_view(), name='change_password'),
    path('logout', LogoutView.as_view(next_page=reverse_lazy('login')), name='logout'),
    path('activate_account/<str:uidb64>/<str:token>', ActivateAccountView.as_view(), name='activate_user'),
    path('reset_password/<str:uidb64>/<str:token>', ResetPasswordView.as_view(), name='reset_password'),
]
