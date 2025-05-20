from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

User = get_user_model()


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff',
                    'is_seller', 'is_buyer', 'email_verified', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'is_seller', 'is_buyer', 'email_verified')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'avatar', 'about')}),
        (_('Roles'), {'fields': ('is_seller', 'is_buyer')}),
        (_('Status'), {'fields': ('email_verified',)}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
        (_('Roles'), {
            'classes': ('wide',),
            'fields': ('is_seller', 'is_buyer'),
        }),
        (_('Permissions'), {
            'classes': ('wide',),
            'fields': ('is_staff', 'is_superuser'),
        }),
    )

    actions = ['make_seller', 'make_buyer', 'verify_email', 'approve_seller']

    def make_seller(self, request, queryset):
        queryset.update(is_seller=True)

    make_seller.short_description = _("Mark selected users as sellers")

    def make_buyer(self, request, queryset):
        queryset.update(is_buyer=True)

    make_buyer.short_description = _("Mark selected users as buyers")

    def verify_email(self, request, queryset):
        queryset.update(email_verified=True, is_active=True)

    verify_email.short_description = _("Verify email for selected users")

    def approve_seller(self, request, queryset):
        queryset.update(is_seller=True, email_verified=True, is_active=True)

    approve_seller.short_description = _("Approve as seller and verify email")