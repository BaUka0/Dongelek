from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from accounts.models import SellerRequest

User = get_user_model()


class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        max_length=254,
        required=True,
        help_text=_('Required. Enter a valid email address.')
    )
    about = forms.CharField(
        widget=forms.Textarea,
        required=False,
        help_text=_('Tell us about yourself.')
    )
    avatar = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'avatar', 'about', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_('This email is already in use.'))
        return email


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label=_("Username or Email"),
        widget=forms.TextInput(attrs={'autofocus': True})
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if '@' in username:
            try:
                user = User.objects.get(email=username)
                return user.username
            except User.DoesNotExist:
                pass
        return username


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'avatar', 'about')


class SellerRequestForm(forms.ModelForm):
    class Meta:
        model = SellerRequest
        fields = ['reason', 'business_description']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Укажите причину, почему вы хотите стать продавцом'}),
            'business_description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Опишите ваш бизнес или опыт продажи автомобилей'})
        }