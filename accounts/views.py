from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.utils.html import strip_tags
from django.views.generic import CreateView, UpdateView
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.contrib import messages
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetConfirmView
from django.db.models import Avg

from Dongelek import settings
from .forms import SignUpForm, CustomAuthenticationForm, ProfileUpdateForm
from .tokens import account_activation_token
from cars.models import SellerReview
from cars.forms import SellerReviewForm

User = get_user_model()


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        current_site = get_current_site(self.request)
        mail_subject = 'Активация аккаунта на сайте Dongelek'

        # HTML версия письма
        html_message = render_to_string('accounts/activation_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
        })

        plain_message = strip_tags(html_message)

        to_email = form.cleaned_data.get('email')

        email = EmailMultiAlternatives(
            mail_subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [to_email]
        )
        email.attach_alternative(html_message, "text/html")
        email.send()

        messages.success(self.request, 'Пожалуйста, подтвердите ваш email для завершения регистрации.')
        return redirect('login')


def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.email_verified = True
        user.save()
        messages.success(request, 'Ваш аккаунт успешно активирован. Теперь вы можете войти.')
        return redirect('login')
    else:
        messages.error(request, 'Ссылка для активации недействительна!')
        return redirect('login')


class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'accounts/login.html'


class CustomPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')
    html_email_template_name = 'accounts/password_reset_email.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ваш профиль успешно обновлен.')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, 'accounts/profile.html', {'form': form})


def profile_detail(request, username):
    profile_user = get_object_or_404(User, username=username)
    
    # Get seller reviews
    seller_reviews = SellerReview.objects.filter(seller=profile_user).order_by('-created_at')
    avg_seller_rating = seller_reviews.aggregate(Avg('rating'))['rating__avg']
    seller_review_count = seller_reviews.count()
    
    # Check if logged-in user has already reviewed this seller
    user_review = None
    if request.user.is_authenticated and request.user != profile_user:
        user_review = SellerReview.objects.filter(reviewer=request.user, seller=profile_user).first()
    
    context = {
        'profile_user': profile_user,
        'seller_reviews': seller_reviews,
        'avg_seller_rating': avg_seller_rating,
        'seller_review_count': seller_review_count,
        'user_review': user_review,
        'seller_review_form': SellerReviewForm(),
        # ... other context items you already have ...
    }
    
    return render(request, 'accounts/profile_detail.html', context)