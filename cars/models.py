from django.db import models
from django.utils.translation import gettext_lazy as _

from Dongelek import settings
from accounts.models import User
from django.urls import reverse
from django.utils.text import slugify


class Brand(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Brand Name"))
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Brand")
        verbose_name_plural = _("Brands")


class CarModel(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name="car_models")
    name = models.CharField(max_length=100, verbose_name=_("Model Name"))
    slug = models.SlugField(blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.brand.name}-{self.name}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.brand.name} {self.name}"

    class Meta:
        verbose_name = _("Car Model")
        verbose_name_plural = _("Car Models")
        unique_together = ('brand', 'name')


class FUEL_CHOICES(models.TextChoices):
    GASOLINE = 'GAS', _('Gasoline')
    DIESEL = 'DIE', _('Diesel')
    ELECTRIC = 'ELE', _('Electric')
    HYBRID = 'HYB', _('Hybrid')
    LPG = 'LPG', _('LPG')


class TRANSMISSION_CHOICES(models.TextChoices):
    MANUAL = 'MAN', _('Manual')
    AUTOMATIC = 'AUT', _('Automatic')
    SEMI_AUTO = 'SMT', _('Semi-Automatic')
    CVT = 'CVT', _('CVT')


class BODY_CHOICES(models.TextChoices):
    SEDAN = 'SED', _('Sedan')
    HATCHBACK = 'HAT', _('Hatchback')
    SUV = 'SUV', _('SUV')
    COUPE = 'CPE', _('Coupe')
    CONVERTIBLE = 'CNV', _('Convertible')
    WAGON = 'WAG', _('Wagon')
    MINIVAN = 'MVN', _('Minivan')
    PICKUP = 'PIC', _('Pickup')


class DRIVE_CHOICES(models.TextChoices):
    FWD = 'FWD', _('Front-Wheel Drive')
    RWD = 'RWD', _('Rear-Wheel Drive')
    AWD = 'AWD', _('All-Wheel Drive')
    _4WD = '4WD', _('4-Wheel Drive')


class Region(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Region Name"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Region")
        verbose_name_plural = _("Regions")


class City(models.Model):
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name="cities")
    name = models.CharField(max_length=100, verbose_name=_("City Name"))

    def __str__(self):
        return f"{self.name}, {self.region.name}"

    class Meta:
        verbose_name = _("City")
        verbose_name_plural = _("Cities")
        unique_together = ('region', 'name')


class Car(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cars")
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name="cars")
    model = models.ForeignKey(CarModel, on_delete=models.PROTECT, related_name="cars")
    year = models.PositiveIntegerField(verbose_name=_("Year"))
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_("Price"))
    mileage = models.PositiveIntegerField(verbose_name=_("Mileage"))
    fuel_type = models.CharField(
        max_length=3,
        choices=FUEL_CHOICES.choices,
        default=FUEL_CHOICES.GASOLINE,
        verbose_name=_("Fuel Type")
    )
    transmission = models.CharField(
        max_length=3,
        choices=TRANSMISSION_CHOICES.choices,
        default=TRANSMISSION_CHOICES.MANUAL,
        verbose_name=_("Transmission")
    )
    body_type = models.CharField(
        max_length=3,
        choices=BODY_CHOICES.choices,
        default=BODY_CHOICES.SEDAN,
        verbose_name=_("Body Type")
    )
    drive_type = models.CharField(
        max_length=3,
        choices=DRIVE_CHOICES.choices,
        default=DRIVE_CHOICES.FWD,
        verbose_name=_("Drive Type")
    )
    color = models.CharField(max_length=50, verbose_name=_("Color"))
    engine_size = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        verbose_name=_("Engine Size (L)"),
        null=True,
        blank=True
    )
    description = models.TextField(verbose_name=_("Description"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    region = models.ForeignKey(
        Region,
        on_delete=models.SET_NULL,
        related_name="cars",
        null=True,
        verbose_name=_("Region")
    )
    city = models.ForeignKey(
        City,
        on_delete=models.SET_NULL,
        related_name="cars",
        null=True,
        verbose_name=_("City")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views_count = models.PositiveIntegerField(default=0, verbose_name=_("Views Count"))
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.brand.name}-{self.model.name}-{self.id}")
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('car_detail', kwargs={'slug': self.slug})

    def get_primary_image(self):
        """Returns the primary image for this car, or the first image if no primary is set."""
        primary = self.images.filter(is_primary=True).first()
        if primary:
            return primary
        return self.images.first()

    def __str__(self):
        return f"{self.brand} {self.model} ({self.year})"

    class Meta:
        verbose_name = _("Car")
        verbose_name_plural = _("Cars")
        ordering = ['-created_at']


class CarImage(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="cars/images/%Y/%m/%d/", verbose_name=_("Image"))
    is_primary = models.BooleanField(default=False, verbose_name=_("Is Primary"))

    def __str__(self):
        return f"Image for {self.car}"

    class Meta:
        verbose_name = _("Car Image")
        verbose_name_plural = _("Car Images")


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorites")
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="favorited_by")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.car}"

    class Meta:
        verbose_name = _("Favorite")
        verbose_name_plural = _("Favorites")
        unique_together = ('user', 'car')


class CompareList(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='compare_list'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Compare list for {self.user.username}"


class CompareItem(models.Model):
    compare_list = models.ForeignKey(
        CompareList, 
        on_delete=models.CASCADE, 
        related_name='items'
    )
    car = models.ForeignKey(
        Car, 
        on_delete=models.CASCADE
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('compare_list', 'car')

    def __str__(self):
        return f"{self.car.brand} {self.car.model} in {self.compare_list}"
