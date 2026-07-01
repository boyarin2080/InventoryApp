from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.generic.edit import FormMixin

from .models import Category
from .forms import CategoryForm


class CategoryListView(LoginRequiredMixin, ListView):
    """View for listing categories with hierarchical display."""
    model = Category
    template_name = 'categories/list.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        """
        Return categories filtered for hierarchical display.
        Root categories (no parent) are shown first.
        """
        queryset = Category.objects.all()
        
        # Filter by search query if provided
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        # Order by parent (None first), then name
        return queryset.order_by('parent', 'name')
    
    def get_context_data(self, **kwargs):
        """Add additional context for template."""
        context = super().get_context_data(**kwargs)
        
        # Get root categories for tree display
        root_categories = Category.objects.filter(parent__isnull=True).order_by('name')
        
        # Build hierarchical tree structure
        def build_tree(category):
            """Recursively build tree structure for category and its children."""
            return {
                'category': category,
                'children': [build_tree(child) for child in 
                           category.children.all().order_by('name')]
            }
        
        category_tree = [build_tree(root) for root in root_categories]
        
        context.update({
            'category_tree': category_tree,
            'search_query': self.request.GET.get('search', ''),
            'root_categories': root_categories,
            'total_categories': Category.objects.count(),
        })
        return context


class CategoryDetailView(LoginRequiredMixin, DetailView):
    """View for displaying category details and hierarchy."""
    model = Category
    template_name = 'categories/detail.html'
    context_object_name = 'category'
    
    def get_context_data(self, **kwargs):
        """Add additional context for template."""
        context = super().get_context_data(**kwargs)
        category = self.object
        
        # Get ancestors for breadcrumb navigation
        ancestors = category.get_ancestors()
        
        # Get immediate children
        children = category.children.all().order_by('name')
        
        # Get all descendants (for statistics)
        descendants = category.get_descendants()
        
        context.update({
            'ancestors': ancestors,
            'children': children,
            'descendants_count': len(descendants),
            'breadcrumb_path': category.get_full_path(),
        })
        return context


class CategoryCreateView(LoginRequiredMixin, CreateView):
    """View for creating new categories."""
    model = Category
    form_class = CategoryForm
    template_name = 'categories/form.html'
    
    def get_success_url(self):
        """Redirect to category detail view after creation."""
        messages.success(self.request, f'Category "{self.object.name}" created successfully.')
        return reverse('categories:detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        """Add additional context for template."""
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Create New Category',
            'submit_button': 'Create Category',
            'parent_id': self.request.GET.get('parent', None),
        })
        return context
    
    def get_initial(self):
        """Set initial form data."""
        initial = super().get_initial()
        
        # Set parent from GET parameter if provided
        parent_id = self.request.GET.get('parent')
        if parent_id:
            try:
                parent = Category.objects.get(pk=parent_id)
                initial['parent'] = parent
            except Category.DoesNotExist:
                pass
        
        return initial


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    """View for updating existing categories."""
    model = Category
    form_class = CategoryForm
    template_name = 'categories/form.html'
    
    def get_success_url(self):
        """Redirect to category detail view after update."""
        messages.success(self.request, f'Category "{self.object.name}" updated successfully.')
        return reverse('categories:detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        """Add additional context for template."""
        context = super().get_context_data(**kwargs)
        context.update({
            'title': f'Edit Category: {self.object.name}',
            'submit_button': 'Update Category',
        })
        return context


class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    """View for deleting categories."""
    model = Category
    template_name = 'categories/delete.html'
    success_url = reverse_lazy('categories:list')
    
    def get_context_data(self, **kwargs):
        """Add additional context for template."""
        context = super().get_context_data(**kwargs)
        category = self.object
        
        # Check if category has children
        children_count = category.children.count()
        
        # Check if category has inventory items
        # Note: This assumes the inventory app is implemented
        inventory_count = 0
        try:
            from inventory.models import InventoryItem
            inventory_count = InventoryItem.objects.filter(category=category).count()
        except ImportError:
            pass
        
        context.update({
            'children_count': children_count,
            'inventory_count': inventory_count,
            'can_delete': (children_count == 0 and inventory_count == 0),
        })
        return context
    
    def delete(self, request, *args, **kwargs):
        """Handle delete with success message."""
        category = self.get_object()
        messages.success(request, f'Category "{category.name}" deleted successfully.')
        return super().delete(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        """Handle POST request for delete."""
        category = self.get_object()
        
        # Check if category has children or inventory items
        children_count = category.children.count()
        
        # Check if category has inventory items
        inventory_count = 0
        try:
            from inventory.models import InventoryItem
            inventory_count = InventoryItem.objects.filter(category=category).count()
        except ImportError:
            pass
        
        if children_count > 0 or inventory_count > 0:
            messages.error(request, 
                f'Cannot delete category "{category.name}". '
                f'It has {children_count} sub-categories and {inventory_count} inventory items.'
            )
            return redirect('categories:detail', pk=category.pk)
        
        return super().post(request, *args, **kwargs)


def category_tree_view(request):
    """View for displaying category tree with hierarchical structure."""
    root_categories = Category.objects.filter(parent__isnull=True).order_by('name')
    
    # Build hierarchical tree structure
    def build_tree(category):
        return {
            'category': category,
            'children': [build_tree(child) for child in 
                       category.children.all().order_by('name')]
        }
    
    category_tree = [build_tree(root) for root in root_categories]
    
    return render(request, 'categories/tree.html', {
        'category_tree': category_tree,
        'total_categories': Category.objects.count(),
    })