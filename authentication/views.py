from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.db.models import Q


@never_cache
def login_view(request):
    """
    Handle user login with Django's built-in authentication.
    Redirects authenticated users away from login page.
    """
    # If user is already authenticated, redirect to dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                
                # Redirect to next parameter if it exists, otherwise to dashboard
                next_url = request.GET.get('next', 'dashboard')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'authentication/login.html', {'form': form})


def logout_view(request):
    """
    Handle user logout.
    GET request shows logout confirmation page.
    POST request performs logout and redirects to login.
    """
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
        return redirect('authentication:login')
    
    # GET request - show logout confirmation page
    return render(request, 'authentication/logout.html')


class DashboardView(TemplateView):
    """
    Dashboard/home page for authenticated users.
    """
    template_name = 'dashboard.html'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        """Add additional context for template."""
        context = super().get_context_data(**kwargs)
        
        # Import models here to avoid circular import
        from inventory.models import InventoryItem
        from sales.models import Sale
        from categories.models import Category
        
        # Get PC Parts category (root level)
        try:
            pc_parts_category = Category.objects.get(name='PC Parts', parent__isnull=True)
            # Get all descendants (subcategories) of PC Parts
            all_pc_parts_categories = [pc_parts_category] + pc_parts_category.get_descendants()
            # Filter items
            pc_parts_items = InventoryItem.objects.filter(
                user=self.request.user,
                category__in=all_pc_parts_categories,
                deleted_at__isnull=True
            )
            # Calculate stats
            total_items = pc_parts_items.count()
            available_items = pc_parts_items.filter(status='available').count()
            in_repair_items = pc_parts_items.filter(status='in_repair').count()
            sold_items = pc_parts_items.filter(status='sold').count()
            total_sales = Sale.objects.filter(inventory_item__in=pc_parts_items).count()
            items_available_message = ""
        except Category.DoesNotExist:
            context['items_available_message'] = "No PC Parts category found."
            context['total_items'] = 0
            context['available_items'] = 0
            context['in_repair_items'] = 0
            context['sold_items'] = 0
            context['total_sales'] = 0
            context['pc_parts_items'] = None
            return context
        
        context.update({
            'total_items': total_items,
            'available_items': available_items,
            'in_repair_items': in_repair_items,
            'sold_items': sold_items,
            'total_sales': total_sales,
            'pc_parts_items': pc_parts_items,
            'items_available_message': items_available_message,
        })
        
        return context