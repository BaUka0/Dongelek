from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import CompareList

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_compare_list(sender, instance, created, **kwargs):
    if created:
        CompareList.objects.create(user=instance)