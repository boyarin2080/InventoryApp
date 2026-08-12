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
        Only active categories are shown.
        """
        queryset = Category.active_categories()

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

        # Get active root categories for tree display
        root_categories = Category.active_categories().filter(parent__isnull=True).order_by('name')

        # Get inactive categories for display at bottom
        inactive_categories = Category.inactive_categories().order_by('name')

        # Build hierarchical tree structure for active categories
        def build_tree(category):
            """Recursively build tree structure for category and its children."""
            return {
                'category': category,
                'children': [build_tree(child) for child in
                           category.children.filter(is_active=True).order_by('name')]
            }

        category_tree = [build_tree(root) for root in root_categories]

        context.update({
            'category_tree': category_tree,
            'inactive_categories': inactive_categories,
            'search_query': self.request.GET.get('search', ''),
            'root_categories': root_categories,
            'total_categories': Category.objects.count(),
            'active_categories_count': Category.active_categories().count(),
            'inactive_categories_count': Category.inactive_categories().count(),
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
        category = self.get_object()

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
    """View for soft-deleting categories."""
    model = Category
    template_name = 'categories/delete.html'
    success_url = reverse_lazy('categories:list')

    def get_object(self, queryset=None):
        """Get the object to delete."""
        obj = super().get_object(queryset)
        return obj

    def get_context_data(self, **kwargs):
        """Add additional context for template."""
        context = super().get_context_data(**kwargs)
        # Ensure object is set before accessing it
        if not hasattr(self, 'object'):
            self.object = self.get_object()
        category = self.object

        # Check if category has children
        children_count = category.children.count()

        # Check if category has non-deleted inventory items
        inventory_count = 0
        try:
            from inventory.models import InventoryItem
            inventory_count = InventoryItem.objects.filter(category=category, deleted_at__isnull=True).count()
        except ImportError:
            pass

        context.update({
            'children_count': children_count,
            'inventory_count': inventory_count,
            'can_soft_delete': True,  # Now categories can always be soft-deleted
        })
        return context

    def delete(self, request, *args, **kwargs):
        """Handle POST request for soft-delete."""
        category = self.get_object()

        # Check if there are any non-deleted inventory items in this category
        try:
            from inventory.models import InventoryItem
            inventory_count = InventoryItem.objects.filter(category=category, deleted_at__isnull=True).count()
        except ImportError:
            inventory_count = 0

        if inventory_count > 0:
            messages.error(request,
                f'Cannot delete category "{category.name}". '
                f'It has {inventory_count} inventory items that are not deleted. '
                'Please delete or move those items first.'
            )
            return redirect('categories:detail', pk=category.pk)

        # Soft delete the category (avoid calling super().delete() which triggers PROTECT error)
        category.soft_delete()
        messages.success(request, f'Category "{category.name}" has been moved to inactive categories.')
        return redirect(self.get_success_url())

    def post(self, request, *args, **kwargs):
        """Override post to handle soft-delete without calling super().delete()."""
        # Set self.object for use in delete() method
        self.object = self.get_object()
        
        # Call delete() which handles soft-delete logic
        # We override this instead of calling super().post() to avoid PROTECT error
        return self.delete(request, *args, **kwargs)


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

