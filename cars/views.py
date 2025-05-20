from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse, NoReverseMatch
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
)
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Q, Avg
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models import (
    Car, CarImage, Favorite, Brand, CarModel, City, Region,
    CompareList, CompareItem, SellerReview
)
from .forms import CarForm, CarImageFormSet, SellerReviewForm

# Get the user model
User = get_user_model()


class CarListView(ListView):
    model = Car
    template_name = 'cars/car_list.html'
    context_object_name = 'cars'
    paginate_by = 12

    def get_queryset(self):
        queryset = Car.objects.filter(is_active=True)

        # Handle search query
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(brand__name__icontains=q) |
                Q(model__name__icontains=q) |
                Q(description__icontains=q)
            )

        # Handle filters
        brand = self.request.GET.get('brand')
        if brand:
            queryset = queryset.filter(brand_id=brand)

        model = self.request.GET.get('model')
        if model:
            queryset = queryset.filter(model_id=model)

        year_from = self.request.GET.get('year_from')
        if year_from:
            queryset = queryset.filter(year__gte=year_from)

        year_to = self.request.GET.get('year_to')
        if year_to:
            queryset = queryset.filter(year__lte=year_to)

        price_from = self.request.GET.get('price_from')
        if price_from:
            queryset = queryset.filter(price__gte=price_from)

        price_to = self.request.GET.get('price_to')
        if price_to:
            queryset = queryset.filter(price__lte=price_to)

        fuel_type = self.request.GET.get('fuel_type')
        if fuel_type:
            queryset = queryset.filter(fuel_type=fuel_type)

        transmission = self.request.GET.get('transmission')
        if transmission:
            queryset = queryset.filter(transmission=transmission)

        region = self.request.GET.get('region')
        if region:
            queryset = queryset.filter(region_id=region)

        city = self.request.GET.get('city')
        if city:
            queryset = queryset.filter(city_id=city)

        # Handle sorting
        sort = self.request.GET.get('sort', '-created_at')
        if sort == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort == 'price_desc':
            queryset = queryset.order_by('-price')
        elif sort == 'year_desc':
            queryset = queryset.order_by('-year')
        elif sort == 'year_asc':
            queryset = queryset.order_by('year')
        elif sort == 'popular':
            queryset = queryset.order_by('-views_count')
        else:
            queryset = queryset.order_by('-created_at')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brands'] = Brand.objects.all()
        context['regions'] = Region.objects.all()

        # Add filter values to context
        for param in self.request.GET:
            if param not in ['page', 'sort']:
                context[param] = self.request.GET.get(param)

        return context


class CarDetailView(DetailView):
    model = Car
    template_name = 'cars/car_detail.html'
    context_object_name = 'car'

    def get_object(self):
        obj = super().get_object()
        # Increment view count
        obj.views_count += 1
        obj.save()
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['is_favorite'] = Favorite.objects.filter(
                user=self.request.user, car=self.object
            ).exists()
            # Check if user has already reviewed this seller
            context['user_review'] = SellerReview.objects.filter(
                reviewer=self.request.user, seller=self.object.seller
            ).first()
        # Add similar cars
        context['similar_cars'] = Car.objects.filter(
            brand=self.object.brand, is_active=True
        ).exclude(id=self.object.id)[:4]
        
        # Add seller rating information
        seller = self.object.seller
        context['seller_reviews'] = SellerReview.objects.filter(seller=seller).order_by('-created_at')
        context['seller_review_form'] = SellerReviewForm()
        context['avg_seller_rating'] = SellerReview.objects.filter(seller=seller).aggregate(Avg('rating'))['rating__avg']
        context['seller_review_count'] = SellerReview.objects.filter(seller=seller).count()
        return context


class CarCreateView(LoginRequiredMixin, CreateView):
    model = Car
    form_class = CarForm
    template_name = 'cars/car_form.html'
    success_url = reverse_lazy('car_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['image_formset'] = CarImageFormSet(
                self.request.POST, 
                self.request.FILES, 
                prefix='images'
            )
        else:
            context['image_formset'] = CarImageFormSet(prefix='images')
        return context

    def form_valid(self, form):
        form.instance.seller = self.request.user
        self.object = form.save()
        
        image_formset = CarImageFormSet(
            self.request.POST, 
            self.request.FILES, 
            instance=self.object,
            prefix='images'
        )
        
        # Debug output
        print(f"FILES: {self.request.FILES}")
        print(f"Formset is valid: {image_formset.is_valid()}")
        
        if image_formset.is_valid():
            # Check if any images were uploaded
            has_images = False
            primary_set = False
            
            # First pass: check if we have images and if a primary is set
            for form in image_formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    image_file = form.cleaned_data.get('image')
                    if image_file:
                        has_images = True
                        if form.cleaned_data.get('is_primary'):
                            primary_set = True
            
            # Second pass: save images and set primary if needed
            saved_images = []
            if has_images:
                for i, form in enumerate(image_formset):
                    if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                        image_file = form.cleaned_data.get('image')
                        if image_file:
                            car_image = form.save(commit=False)
                            car_image.car = self.object
                            
                            # If no primary is set, make the first image primary
                            if i == 0 and not primary_set:
                                car_image.is_primary = True
                                
                            car_image.save()
                            saved_images.append(car_image)
                            print(f"Saved image: {car_image.pk} - Primary: {car_image.is_primary}")
            
            # Add a message to indicate if images were saved
            if saved_images:
                messages.success(self.request, f"Car listing created with {len(saved_images)} images.")
            else:
                messages.warning(self.request, "Car listing created without images. You can add images later by editing the listing.")
                
            return redirect(self.get_success_url())
        else:
            print(f"Formset errors: {image_formset.errors}")
            print(f"Non-form errors: {image_formset.non_form_errors()}")
            
        return super().form_valid(form)

    def form_invalid(self, form):
        print(f"Form errors: {form.errors}")
        return self.render_to_response(self.get_context_data(form=form))


class CarUpdateView(LoginRequiredMixin, UpdateView):
    model = Car
    form_class = CarForm
    template_name = 'cars/car_form.html'

    def get_queryset(self):
        # Only allow users to edit their own cars
        return Car.objects.filter(seller=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['image_formset'] = CarImageFormSet(
                self.request.POST, 
                self.request.FILES, 
                instance=self.object,
                prefix='images'
            )
        else:
            context['image_formset'] = CarImageFormSet(
                instance=self.object,
                prefix='images'
            )
        return context

    def form_valid(self, form):
        self.object = form.save()
        
        image_formset = CarImageFormSet(
            self.request.POST, 
            self.request.FILES, 
            instance=self.object,
            prefix='images'
        )
        
        # Debug output
        print(f"UPDATE - FILES: {self.request.FILES}")
        print(f"UPDATE - Formset is valid: {image_formset.is_valid()}")
        
        if image_formset.is_valid():
            # First, save the formset to process deletions
            instances = image_formset.save(commit=False)
            
            # Handle new instances
            primary_exists = False
            for instance in instances:
                instance.car = self.object
                if instance.is_primary:
                    primary_exists = True
                instance.save()
                print(f"Saved/updated image: {instance.pk} - Primary: {instance.is_primary}")
                
            # Process deletions
            for obj in image_formset.deleted_objects:
                print(f"Deleting image: {obj.pk}")
                obj.delete()
                
            # If no image is marked as primary but we have images, set the first one as primary
            if not primary_exists and self.object.images.exists():
                first_image = self.object.images.first()
                first_image.is_primary = True
                first_image.save()
                print(f"Set image {first_image.pk} as primary")
                
            messages.success(self.request, "Car listing updated successfully.")
            
            return redirect(self.object.get_absolute_url())
        else:
            print(f"UPDATE - Formset errors: {image_formset.errors}")
            print(f"UPDATE - Non-form errors: {image_formset.non_form_errors()}")
            
        return super().form_valid(form)

    def form_invalid(self, form):
        print(f"Update main form errors: {form.errors}")
        context = self.get_context_data(form=form)
        image_formset = context['image_formset']
        
        if not image_formset.is_valid():
            print(f"Update image formset errors: {image_formset.errors}")
            print(f"Update image formset non-form errors: {image_formset.non_form_errors()}")
            
        return self.render_to_response(context)


class CarDeleteView(LoginRequiredMixin, DeleteView):
    model = Car
    template_name = 'cars/car_confirm_delete.html'
    success_url = reverse_lazy('car_list')

    def get_queryset(self):
        # Only allow users to delete their own cars
        return Car.objects.filter(seller=self.request.user)


@login_required
@require_POST
def toggle_favorite(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    favorite, created = Favorite.objects.get_or_create(
        user=request.user, car=car
    )

    if not created:
        favorite.delete()
        is_favorite = False
    else:
        is_favorite = True

    # Add more debugging info to the response
    return JsonResponse({
        'success': True,
        'is_favorite': is_favorite,
        'car_id': car_id
    })


def load_models(request):
    brand_id = request.GET.get('brand')
    models = CarModel.objects.filter(brand_id=brand_id).order_by('name')
    return JsonResponse({
        'models': [{'id': model.id, 'name': model.name} for model in models]
    })


def load_cities(request):
    region_id = request.GET.get('region')
    cities = City.objects.filter(region_id=region_id).order_by('name')
    return JsonResponse({
        'cities': [{'id': city.id, 'name': city.name} for city in cities]
    })


@login_required
@require_POST
def create_brand(request):
    brand_name = request.POST.get('brand_name')
    if not brand_name:
        return JsonResponse({'success': False, 'error': 'Brand name is required'})

    # Check if brand already exists
    if Brand.objects.filter(name=brand_name).exists():
        return JsonResponse({'success': False, 'error': 'Brand already exists'})

    # Create new brand
    brand = Brand.objects.create(name=brand_name)
    return JsonResponse({
        'success': True,
        'id': brand.id,
        'name': brand.name
    })


@login_required
@require_POST
def create_model(request):
    model_name = request.POST.get('model_name')
    brand_id = request.POST.get('brand_id')
    
    if not model_name or not brand_id:
        return JsonResponse({'success': False, 'error': 'Model name and brand are required'})
    
    try:
        brand = Brand.objects.get(id=brand_id)
    except Brand.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Selected brand does not exist'})
    
    # Check if model already exists for this brand
    if CarModel.objects.filter(name=model_name, brand=brand).exists():
        return JsonResponse({'success': False, 'error': 'This model already exists for the selected brand'})
    
    # Create new model
    model = CarModel.objects.create(name=model_name, brand=brand)
    return JsonResponse({
        'success': True,
        'id': model.id,
        'name': model.name
    })


class FavoriteListView(LoginRequiredMixin, ListView):
    model = Favorite
    template_name = 'cars/favorite_list.html'
    context_object_name = 'favorites'

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add any additional context needed for the favorites page
        return context


@login_required
def add_to_compare(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    compare_list, created = CompareList.objects.get_or_create(user=request.user)
    
    # Check if car already in compare list
    if compare_list.items.filter(car=car).exists():
        messages.info(request, f"{car.brand} {car.model} уже добавлен в список сравнения")
    else:
        # Check if compare list has less than 5 items
        if compare_list.items.count() >= 5:
            messages.warning(request, "Можно сравнивать максимум 5 автомобилей. Удалите один из автомобилей, чтобы добавить новый.")
        else:
            CompareItem.objects.create(compare_list=compare_list, car=car)
            messages.success(request, f"{car.brand} {car.model} добавлен в список сравнения")
    
    next_url = request.GET.get('next', 'compare_list')
    return redirect(next_url)

@login_required
def remove_from_compare(request, car_id):
    compare_list = get_object_or_404(CompareList, user=request.user)
    item = compare_list.items.filter(car__id=car_id).first()
    
    if item:
        car_name = f"{item.car.brand} {item.car.model}"
        item.delete()
        messages.success(request, f"{car_name} удален из списка сравнения")
    
    return redirect('compare_list')

@login_required
def compare_list(request):
    compare_list, created = CompareList.objects.get_or_create(user=request.user)
    cars = [item.car for item in compare_list.items.select_related('car').order_by('added_at')]
    
    # Handle AJAX requests for the compare count
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'cars/compare_list.html', {'cars': cars})
    
    return render(request, 'cars/compare_list.html', {'cars': cars})


@login_required
def add_seller_review(request, seller_id):
    seller = get_object_or_404(User, id=seller_id)
    
    # Check if the user is not trying to review themselves
    if seller == request.user:
        messages.error(request, "You cannot review yourself.")
        # Try different possible URL names or use a safe fallback
        try:
            return redirect('user_profile', username=seller.username)
        except NoReverseMatch:
            try:
                return redirect('accounts:profile_detail', username=seller.username)
            except NoReverseMatch:
                # If no profile view is available, redirect to home
                return redirect('home')
    
    # Check if user has already reviewed this seller
    existing_review = SellerReview.objects.filter(reviewer=request.user, seller=seller).first()
    
    # Get the optional car_id if provided
    car_id = request.POST.get('car_id')
    car = None
    if car_id:
        try:
            car = Car.objects.get(id=car_id, seller=seller)
        except Car.DoesNotExist:
            pass
    
    if request.method == 'POST':
        form = SellerReviewForm(request.POST, instance=existing_review)
        if form.is_valid():
            review = form.save(commit=False)
            if not existing_review:
                review.reviewer = request.user
                review.seller = seller
                review.car = car
                
                # Check if user has interacted with the seller (e.g., sent a message)
                if hasattr(request.user, 'conversations'):
                    if request.user.conversations.filter(participants=seller).exists():
                        review.is_verified = True
            
            review.save()
            
            if existing_review:
                messages.success(request, "Your review has been updated.")
            else:
                messages.success(request, "Your review has been submitted.")
            
            # Redirect back to where the review was submitted from
            next_url = request.POST.get('next', '')
            if next_url:
                return redirect(next_url)
            else:
                # Try different possible URL names or use a safe fallback
                try:
                    return redirect('user_profile', username=seller.username)
                except NoReverseMatch:
                    # If profile view not found, redirect to car detail or home
                    if car:
                        return redirect('car_detail', slug=car.slug)
                    else:
                        return redirect('home')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    
    # If GET request or form invalid, redirect back
    if request.META.get('HTTP_REFERER'):
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        # Simple fallback if no referrer
        if car:
            return redirect('car_detail', slug=car.slug)
        else:
            return redirect('home')


@login_required
def delete_seller_review(request, review_id):
    review = get_object_or_404(SellerReview, id=review_id)
    
    # Check if the user is the owner of the review
    if review.reviewer != request.user:
        messages.error(request, "You cannot delete someone else's review.")
        # Try different possible URL names or use a safe fallback
        try:
            return redirect('user_profile', username=review.seller.username)
        except NoReverseMatch:
            if hasattr(review, 'car') and review.car:
                return redirect('car_detail', slug=review.car.slug)
            else:
                return redirect('home')
    
    if request.method == 'POST':
        seller_username = review.seller.username
        # Save car reference before deleting review
        car = review.car
        review.delete()
        messages.success(request, "Your review has been deleted.")
        
        # Redirect back to where the review was deleted from
        next_url = request.POST.get('next', '')
        if next_url:
            return redirect(next_url)
        else:
            # Try different possible URL names or use a safe fallback
            try:
                return redirect('user_profile', username=seller_username)
            except NoReverseMatch:
                if car:
                    return redirect('car_detail', slug=car.slug)
                else:
                    return redirect('home')
    
    context = {
        'review': review,
        'next': request.GET.get('next', '')
    }
    return render(request, 'cars/seller_review_confirm_delete.html', context)