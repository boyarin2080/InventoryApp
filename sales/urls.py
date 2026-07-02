from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    # Sales list view
    path('', views.SaleListView.as_view(), name='list'),
    
    # Sale CRUD operations
    path('create/', views.SaleCreateView.as_view(), name='create'),
    path('<int:pk>/', views.SaleDetailView.as_view(), name='detail'),
    # path('<int:pk>/edit/', views.SaleUpdateView.as_view(), name='update'),
    # path('<int:pk>/delete/', views.SaleDeleteView.as_view(), name='delete'),
]
