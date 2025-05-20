from django.urls import path
from . import views

urlpatterns = [
    path('', views.CarListView.as_view(), name='car_list'),
    path('create/', views.CarCreateView.as_view(), name='car_create'),
    path('compare/', views.compare_list, name='compare_list'),
    path('<slug:slug>/', views.CarDetailView.as_view(), name='car_detail'),
    path('<slug:slug>/update/', views.CarUpdateView.as_view(), name='car_update'),
    path('<slug:slug>/delete/', views.CarDeleteView.as_view(), name='car_delete'),
    
    # Favorites
    path('favorite/list/', views.FavoriteListView.as_view(), name='favorite_list'),
    path('favorite/<int:car_id>/', views.toggle_favorite, name='toggle_favorite'),

    # Compare
    path('compare/add/<int:car_id>/', views.add_to_compare, name='add_to_compare'),
    path('compare/remove/<int:car_id>/', views.remove_from_compare, name='remove_from_compare'),
    
    # AJAX
    path('ajax/load-models/', views.load_models, name='ajax_load_models'),
    path('ajax/load-cities/', views.load_cities, name='ajax_load_cities'),
    path('ajax/create-brand/', views.create_brand, name='ajax_create_brand'),
    path('ajax/create-model/', views.create_model, name='ajax_create_model'),
]