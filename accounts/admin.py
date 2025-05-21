from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import SellerRequest

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


class SellerRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__email', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Информация о заявке', {
            'fields': ('user', 'reason', 'business_description', 'status')
        }),
        ('Дополнительная информация', {
            'fields': ('admin_notes', 'created_at', 'updated_at')
        }),
    )
    actions = ['approve_requests', 'reject_requests']
    
    def approve_requests(self, request, queryset):
        approved_count = 0
        for seller_request in queryset:
            if seller_request.status != 'approved':  # Only approve if not already approved
                seller_request.approve()  # This method updates user to seller
                approved_count += 1
        
        if approved_count > 0:
            self.message_user(request, f"{approved_count} заявок было одобрено. Пользователи получили статус продавцов.")
        else:
            self.message_user(request, "Нет новых заявок для одобрения.")
    approve_requests.short_description = "Одобрить выбранные заявки и сделать пользователей продавцами"
    
    def reject_requests(self, request, queryset):
        for seller_request in queryset:
            seller_request.reject()
        self.message_user(request, f"{queryset.count()} заявок было отклонено.")
    reject_requests.short_description = "Отклонить выбранные заявки"

    def save_model(self, request, obj, form, change):
        if change:  # If this is an edit (not a new object)
            original_obj = SellerRequest.objects.get(pk=obj.pk)
            # Check if status was changed to 'approved'
            if original_obj.status != 'approved' and obj.status == 'approved':
                # Call the approve method which will make the user a seller
                obj.save()  # First save to update the status
                obj.approve()
                self.message_user(request, f"Заявка одобрена. Пользователь {obj.user.username} получил статус продавца.")
            # Check if status was changed to 'rejected'
            elif original_obj.status != 'rejected' and obj.status == 'rejected':
                # Call the reject method
                obj.save()  # First save to update the status
                obj.reject()
                self.message_user(request, f"Заявка отклонена.")
            else:
                # Normal save for other changes
                super().save_model(request, obj, form, change)
        else:
            # This is a new object
            super().save_model(request, obj, form, change)

admin.site.register(SellerRequest, SellerRequestAdmin)