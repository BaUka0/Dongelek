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


class SellerRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'На рассмотрении'),
        ('approved', 'Одобрено'),
        ('rejected', 'Отклонено')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seller_requests')
    reason = models.TextField(verbose_name="Причина запроса")
    business_description = models.TextField(verbose_name="Описание бизнеса", blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    admin_notes = models.TextField(blank=True, null=True, verbose_name="Заметки администратора")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Заявка на статус продавца"
        verbose_name_plural = "Заявки на статус продавца"
    
    def __str__(self):
        return f"Заявка от {self.user.email} ({self.get_status_display()})"
    
    def approve(self):
        """Approve the request and update user to seller."""
        self.status = 'approved'
        self.save()
        
        # Update user profile to be a seller
        self.user.is_seller = True
        self.user.is_buyer = False  # Optional: make user exclusively a seller
        self.user.save()
        
        return True
    
    def reject(self):
        """Reject the request."""
        self.status = 'rejected'
        self.save()
        return True