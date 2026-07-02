from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # Inventory item list view
    path('', views.InventoryItemListView.as_view(), name='list'),
    
    # Inventory item CRUD operations
    path('create/', views.InventoryItemCreateView.as_view(), name='create'),
    path('<int:pk>/', views.InventoryItemDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.InventoryItemUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.InventoryItemDeleteView.as_view(), name='delete'),
]
