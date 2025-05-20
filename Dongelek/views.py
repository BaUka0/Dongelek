from django.shortcuts import render
from cars.models import Car, Brand


def home(request):
    # Get latest cars
    latest_cars = Car.objects.filter(is_active=True).order_by('-created_at')[:8]

    # Get popular cars (most viewed)
    popular_cars = Car.objects.filter(is_active=True).order_by('-views_count')[:8]

    # Get all car brands for the search form
    brands = Brand.objects.all()

    return render(request, 'home.html', {
        'latest_cars': latest_cars,
        'popular_cars': popular_cars,
        'brands': brands
    })