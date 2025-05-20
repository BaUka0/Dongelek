from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    about = models.TextField(_('about'), blank=True)
    email_verified = models.BooleanField(default=False)

    is_seller = models.BooleanField(default=False)
    is_buyer = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.username