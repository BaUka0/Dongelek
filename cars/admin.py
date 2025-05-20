from django.contrib import admin
from .models import (
    Brand, CarModel, Car, CarImage, Favorite, Region, City, 
    CompareList, CompareItem, SellerReview
)


class CarModelInline(admin.TabularInline):
    model = CarModel
    extra = 0


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    inlines = [CarModelInline]


@admin.register(CarModel)
class CarModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand')
    list_filter = ('brand',)
    search_fields = ('name', 'brand__name')


class CityInline(admin.TabularInline):
    model = City
    extra = 0


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    inlines = [CityInline]


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'region')
    list_filter = ('region',)
    search_fields = ('name', 'region__name')


class CarImageInline(admin.TabularInline):
    model = CarImage
    extra = 0


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'seller', 'price', 'year', 'is_active', 'created_at')
    list_filter = ('brand', 'model', 'fuel_type', 'transmission', 'body_type', 'is_active', 'region')
    search_fields = ('brand__name', 'model__name', 'description', 'seller__email')
    readonly_fields = ('views_count', 'created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('seller', 'brand', 'model', 'year', 'price', 'slug')
        }),
        ('Car Details', {
            'fields': ('mileage', 'fuel_type', 'transmission', 'body_type', 'drive_type',
                      'color', 'engine_size', 'description')
        }),
        ('Location', {
            'fields': ('region', 'city')
        }),
        ('Status', {
            'fields': ('is_active', 'views_count', 'created_at', 'updated_at')
        }),
    )
    inlines = [CarImageInline]


@admin.register(CarImage)
class CarImageAdmin(admin.ModelAdmin):
    list_display = ('car', 'is_primary')
    list_filter = ('is_primary',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'car', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'car__brand__name', 'car__model__name')


class CompareItemInline(admin.TabularInline):
    model = CompareItem
    extra = 1
    readonly_fields = ('added_at',)
    autocomplete_fields = ['car']


@admin.register(CompareList)
class CompareListAdmin(admin.ModelAdmin):
    list_display = ('user', 'id', 'items_count')
    search_fields = ('user__email', 'user__username')
    inlines = [CompareItemInline]

    def items_count(self, obj):
        return obj.items.count()

    items_count.short_description = 'Количество автомобилей'


@admin.register(CompareItem)
class CompareItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'compare_list', 'car', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('compare_list__user__email', 'car__brand__name', 'car__model__name')
    autocomplete_fields = ['car', 'compare_list']
    readonly_fields = ('added_at',)


@admin.register(SellerReview)
class SellerReviewAdmin(admin.ModelAdmin):
    list_display = ('reviewer', 'seller', 'rating', 'is_verified', 'created_at')
    list_filter = ('rating', 'is_verified', 'created_at')
    search_fields = ('reviewer__username', 'seller__username', 'comment')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Review Information', {
            'fields': ('reviewer', 'seller', 'car', 'rating', 'comment')
        }),
        ('Verification', {
            'fields': ('is_verified',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )