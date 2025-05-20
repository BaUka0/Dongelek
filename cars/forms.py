from django import forms
from .models import Car, CarImage, Brand, CarModel, City, Region, SellerReview
from django.utils.translation import gettext_lazy as _


class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = [
            'brand', 'model', 'year', 'price', 'mileage',
            'fuel_type', 'transmission', 'body_type', 'drive_type',
            'color', 'engine_size', 'description', 'region', 'city'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['model'].queryset = CarModel.objects.none()
        self.fields['city'].queryset = City.objects.none()

        if 'brand' in self.data:
            try:
                brand_id = int(self.data.get('brand'))
                self.fields['model'].queryset = CarModel.objects.filter(brand_id=brand_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['model'].queryset = self.instance.brand.car_models.all()

        if 'region' in self.data:
            try:
                region_id = int(self.data.get('region'))
                self.fields['city'].queryset = City.objects.filter(region_id=region_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['city'].queryset = self.instance.region.cities.all()


class CarImageForm(forms.ModelForm):
    class Meta:
        model = CarImage
        fields = ['image', 'is_primary']
        
    def clean_is_primary(self):
        # Get the cleaned data
        is_primary = self.cleaned_data.get('is_primary')
        image = self.cleaned_data.get('image')
        
        # If this form is being deleted, don't validate is_primary
        if self.cleaned_data.get('DELETE', False):
            return is_primary
            
        # If no image is provided and this is a new form, skip validation
        if not image and not self.instance.pk:
            return is_primary
            
        return is_primary


# The 'prefix' parameter is not supported by inlineformset_factory
# Remove it and set the prefix when creating the formset instance in the view
CarImageFormSet = forms.inlineformset_factory(
    Car, CarImage, form=CarImageForm,
    extra=1, can_delete=True, max_num=10,
    validate_max=True
)


class SellerReviewForm(forms.ModelForm):
    class Meta:
        model = SellerReview
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-select'}),
            'comment': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4, 
                'placeholder': 'Share your experience with this seller...'
            }),
        }