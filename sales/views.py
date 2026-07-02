from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .models import Sale
from inventory.models import InventoryItem


class SaleListView(LoginRequiredMixin, ListView):
    """View for listing sales with user-based filtering."""
    model = Sale
    template_name = 'sales/list.html'
    context_object_name = 'sales'
    paginate_by = 10
    
    def get_queryset(self):
        """Return sales filtered by current user's inventory items."""
        queryset = Sale.objects.filter(inventory_item__user=self.request.user)
        
        # Filter by date range if provided
        start_date = self.request.GET.get('start_date', '')
        end_date = self.request.GET.get('end_date', '')
        if start_date:
            from django.utils import timezone
            queryset = queryset.filter(sale_date__gte=start_date)
        if end_date:
            from django.utils import timezone
            queryset = queryset.filter(sale_date__lte=end_date)
        
        return queryset.order_by('-sale_date', '-created_at')
    
    def get_context_data(self, **kwargs):
        """Add additional context for template."""
        context = super().get_context_data(**kwargs)
        
        # Calculate total sales and profit
        from decimal import Decimal
        total_sales = Decimal('0.00')
        total_profit = Decimal('0.00')
        
        for sale in self.get_queryset():
            total_sales += sale.sale_price
            total_profit += sale.calculate_profit()
        
        context.update({
            'total_sales': total_sales,
            'total_profit': total_profit,
            'start_date': self.request.GET.get('start_date', ''),
            'end_date': self.request.GET.get('end_date', ''),
        })
        return context


class SaleDetailView(LoginRequiredMixin, DetailView):
    """View for displaying sale details."""
    model = Sale
    template_name = 'sales/detail.html'
    context_object_name = 'sale'
    
    def get_queryset(self):
        """Ensure user can only view their own sales."""
        return Sale.objects.filter(inventory_item__user=self.request.user)
    
    def get_context_data(self, **kwargs):
        """Add additional context for template."""
        context = super().get_context_data(**kwargs)
        sale = self.object
        
        context.update({
            'profit': sale.calculate_profit(),
            'profit_margin': sale.calculate_profit_margin(),
            'profit_category': sale.get_profit_category(),
            'is_profitable': sale.is_profitable(),
        })
        return context


class SaleCreateView(LoginRequiredMixin, CreateView):
    """View for creating new sales."""
    model = Sale
    template_name = 'sales/form.html'
    fields = ['inventory_item', 'sale_date', 'sale_price', 'notes']
    
    def get_success_url(self):
        """Redirect to sale detail view after creation."""
        messages.success(self.request, f'Sale of "{self.object.inventory_item.name}" recorded successfully.')
        return reverse('sales:detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        """Add additional context for template."""
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Record Sale',
            'submit_button': 'Record Sale',
        })
        return context
    
    def get_initial(self):
        """Set initial form data."""
        initial = super().get_initial()
        
        # Set sale date to today
        from django.utils import timezone
        initial['sale_date'] = timezone.now().date()
        
        # Set inventory item from GET parameter if provided
        inventory_item_id = self.request.GET.get('inventory_item')
        if inventory_item_id:
            try:
                initial['inventory_item'] = InventoryItem.objects.get(
                    pk=inventory_item_id,
                    user=self.request.user
                )
            except InventoryItem.DoesNotExist:
                pass
        
        return initial
    
    def get_form(self, form_class=None):
        """Get form with inventory item choices filtered by current user."""
        form = super().get_form(form_class)
        
        # Only show inventory items that belong to the current user
        form.fields['inventory_item'].queryset = InventoryItem.objects.filter(
            user=self.request.user
        ).filter(status__in=['available', 'in_repair'])
        
        return form
    
    def form_valid(self, form):
        """Validate form and set inventory item user."""
        # Get the inventory item to check ownership
        inventory_item = form.cleaned_data.get('inventory_item')
        
        # Ensure the inventory item belongs to the current user
        if inventory_item.user != self.request.user:
            messages.error(self.request, 'You can only record sales for your own inventory items.')
            return redirect('sales:create')
        
        # Ensure the item is available or in repair
        if not inventory_item.can_be_sold():
            messages.error(self.request, 'This item cannot be sold (status: {})'.format(
                inventory_item.get_status_display()
            ))
            return redirect('sales:create')
        
        return super().form_valid(form)


class SaleUpdateView(LoginRequiredMixin, UpdateView):
    """View for updating existing sales."""
    model = Sale
    template_name = 'sales/form.html'
    fields = ['sale_date', 'sale_price', 'notes']
    
    def get_queryset(self):
        """Ensure user can only edit their own sales."""
        return Sale.objects.filter(inventory_item__user=self.request.user)
    
    def get_success_url(self):
        """Redirect to sale detail view after update."""
        messages.success(self.request, f'Sale updated successfully.')
        return reverse('sales:detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        """Add additional context for template."""
        context = super().get_context_data(**kwargs)
        context.update({
            'title': f'Edit Sale: {self.object.inventory_item.name}',
            'submit_button': 'Update Sale',
        })
        return context


class SaleDeleteView(LoginRequiredMixin, DeleteView):
    """View for deleting sales."""
    model = Sale
    template_name = 'sales/delete.html'
    success_url = reverse_lazy('sales:list')
    
    def get_queryset(self):
        """Ensure user can only delete their own sales."""
        return Sale.objects.filter(inventory_item__user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        """Handle delete with success message."""
        sale = self.get_object()
        messages.success(request, f'Sale of "{sale.inventory_item.name}" deleted successfully.')
        return super().delete(request, *args, **kwargs)
