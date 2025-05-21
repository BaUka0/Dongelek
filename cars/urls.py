from django.urls import path
from . import views

urlpatterns = [
    path('', views.CarListView.as_view(), name='car_list'),
    path('create/', views.CarCreateView.as_view(), name='car_create'),
    path('compare/', views.compare_list, name='compare_list'),
    # Dashboard routes
    path('dashboard/', views.SellerDashboardView.as_view(), name='seller_dashboard'),
    path('dashboard/chart-data/', views.dashboard_chart_data, name='dashboard_chart_data'),
    path('toggle-status/<slug:slug>/', views.toggle_car_status, name='toggle_car_status'),

    
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

    # Seller Reviews
    path('seller/<int:seller_id>/review/', views.add_seller_review, name='add_seller_review'),
    path('seller/review/<int:review_id>/delete/', views.delete_seller_review, name='delete_seller_review'),

    
]