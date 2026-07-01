from django.urls import path
from . import views

app_name = 'categories'

urlpatterns = [
    # Category list and tree views
    path('', views.CategoryListView.as_view(), name='list'),
    path('tree/', views.category_tree_view, name='tree'),
    
    # Category CRUD operations
    path('create/', views.CategoryCreateView.as_view(), name='create'),
    path('<int:pk>/', views.CategoryDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='delete'),
]