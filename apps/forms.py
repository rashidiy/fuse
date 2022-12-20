from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.hashers import make_password
from django.contrib.auth.views import PasswordResetView
from django.core.exceptions import ValidationError
from django.forms import CharField, ModelForm, PasswordInput, Form, EmailField
from django.views.generic import TemplateView

from apps.models import User, Post, Contact


class LoginPageForm(AuthenticationForm):
    def clean_username(self):
        return self.cleaned_data.get('username').lower()

    def clean(self):
        user = User.objects.filter(username=self.clean_username()).first()
        if user and not user.is_active:
            raise ValidationError(f'We sent activation link your email ({user.email}) activate then log in again')

        return super().clean()


class RegisterForm(ModelForm):
    verify_password = CharField(widget=PasswordInput(attrs={"autocomplete": "current-password"}))

    def clean_username(self):
        return self.cleaned_data.get('username').lower()

    def clean_password(self):
        password = self.cleaned_data['password']
        confirm_password = self.data['verify_password']
        if confirm_password != password:
            raise ValidationError('Parolni takshiring!')
        return make_password(password)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password')


class PostQueueForm(ModelForm):
    class Meta:
        model = Post
        exclude = ('slug', 'status', 'created_at', 'updated_at', 'views_count')


class SearchBoxForm(Form):
    like = CharField()


class ContactForm(ModelForm):
    username = CharField(max_length=225)

    class Meta:
        model = Contact
        exclude = ('user',)


class AccountSettingsForm(ModelForm):
    class Meta:
        model = User
        exclude = ()


class ForgetPasswordForm(Form):
    email = EmailField()

    def clean_email(self):
        email = self.cleaned_data.get('email')
        user = User.objects.filter(email=email).first()
        if not user:
            return ValidationError('Bu email bilan ro\'yxatdan o\'tgan user topilmadi')
        return email


class UserPasswordResetView(TemplateView):
    template_name = 'apps/auth/reset_password.html'

