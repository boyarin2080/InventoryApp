from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .models import InventoryItem
from .forms import InventoryItemForm


class InventoryItemListView(LoginRequiredMixin, ListView):
    """View for listing inventory items with user-based filtering."""
    model = InventoryItem
    template_name = 'inventory/list.html'
    context_object_name = 'inventory_items'
    paginate_by = 10
    
    def get_queryset(self):
        """Return inventory items filtered by current user."""
        queryset = InventoryItem.objects.filter(user=self.request.user)
        
        # Filter by status if provided
        status = self.request.GET.get('status', '')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by category if provided
        category = self.request.GET.get('category', '')
        if category:
            queryset = queryset.filter(category__id=category)
        
        # Search by name or description
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                name__icontains=search_query
            ) | queryset.filter(description__icontains=search_query)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        """Add additional context for template."""
        context = super().get_context_data(**kwargs)
        
        # Get unique categories for filtering
        from categories.models import Category
        categories = Category.objects.all().order_by('name')
        
        # Get status choices for filtering
        status_choices = InventoryItem.STATUS_CHOICES
        
        # Get filter parameters
        context.update({
            'categories': categories,
            'status_choices': status_choices,
            'current_status': self.request.GET.get('status', ''),
            'current_category': self.request.GET.get('category', ''),
            'search_query': self.request.GET.get('search', ''),
            'total_items': InventoryItem.objects.filter(user=self.request.user).count(),
            'available_items': InventoryItem.objects.filter(user=self.request.user, status='available').count(),
            'in_repair_items': InventoryItem.objects.filter(user=self.request.user, status='in_repair').count(),
            'sold_items': InventoryItem.objects.filter(user=self.request.user, status='sold').count(),
        })
        return context


class InventoryItemDetailView(LoginRequiredMixin, DetailView):
    """View for displaying inventory item details."""
    model = InventoryItem
    template_name = 'inventory/detail.html'
    context_object_name = 'inventory_item'
    
    def get_queryset(self):
        """Ensure user can only view their own inventory items."""
        return InventoryItem.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        """Add additional context for template."""
        context = super().get_context_data(**kwargs)
        item = self.object
        
        context.update({
            'can_be_sold': item.can_be_sold(),
            'is_sold': item.is_sold(),
            'is_available': item.is_available(),
        })
        return context


class InventoryItemCreateView(LoginRequiredMixin, CreateView):
    """View for creating new inventory items."""
    model = InventoryItem
    form_class = InventoryItemForm
    template_name = 'inventory/form.html'
    
    def get_success_url(self):
        """Redirect to inventory item detail view after creation."""
        messages.success(self.request, f'Inventory item "{self.object.name}" created successfully.')
        return reverse('inventory:detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        """Add additional context for template."""
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Create New Inventory Item',
            'submit_button': 'Create Item',
        })
        return context
    
    def form_valid(self, form):
        """Set the user before saving the form."""
        form.instance.user = self.request.user
        return super().form_valid(form)


class InventoryItemUpdateView(LoginRequiredMixin, UpdateView):
    """View for updating existing inventory items."""
    model = InventoryItem
    form_class = InventoryItemForm
    template_name = 'inventory/form.html'
    
    def get_queryset(self):
        """Ensure user can only edit their own inventory items."""
        return InventoryItem.objects.filter(user=self.request.user)
    
    def get_success_url(self):
        """Redirect to inventory item detail view after update."""
        messages.success(self.request, f'Inventory item "{self.object.name}" updated successfully.')
        return reverse('inventory:detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        """Add additional context for template."""
        context = super().get_context_data(**kwargs)
        context.update({
            'title': f'Edit Inventory Item: {self.object.name}',
            'submit_button': 'Update Item',
        })
        return context


class InventoryItemDeleteView(LoginRequiredMixin, DeleteView):
    """View for deleting inventory items."""
    model = InventoryItem
    template_name = 'inventory/delete.html'
    success_url = reverse_lazy('inventory:list')
    
    def get_queryset(self):
        """Ensure user can only delete their own inventory items."""
        return InventoryItem.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        """Handle delete with success message."""
        inventory_item = self.get_object()
        messages.success(request, f'Inventory item "{inventory_item.name}" deleted successfully.')
        return super().delete(request, *args, **kwargs)
