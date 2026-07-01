from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import InventoryItem


class InventoryItemAdmin(admin.ModelAdmin):
    """Admin configuration for InventoryItem model."""
    
    list_display = (
        'name', 
        'user_link', 
        'category_link', 
        'status_badge', 
        'purchase_price_display',
        'purchase_date', 
        'created_at'
    )
    list_filter = (
        'status', 
        'category', 
        'purchase_date', 
        'created_at',
        'user'
    )
    search_fields = (
        'name', 
        'description', 
        'characteristics',
        'user__username',
        'user__email'
    )
    ordering = ('-created_at',)
    readonly_fields = (
        'created_at', 
        'updated_at', 
        'characteristics_display',
        'is_sold_display',
        'is_available_display'
    )
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'user', 'category')
        }),
        ('Purchase Details', {
            'fields': ('purchase_date', 'purchase_price')
        }),
        ('Status & Characteristics', {
            'fields': ('status', 'characteristics')
        }),
        ('Read-only Information', {
            'fields': (
                'characteristics_display',
                'is_sold_display',
                'is_available_display',
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def user_link(self, obj):
        """Display user as a clickable link."""
        if obj.user:
            url = f'/admin/authentication/user/{obj.user.id}/change/'
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return "—"
    user_link.short_description = 'User'
    user_link.admin_order_field = 'user__username'
    
    def category_link(self, obj):
        """Display category as a clickable link."""
        if obj.category:
            url = f'/admin/categories/category/{obj.category.id}/change/'
            return format_html('<a href="{}">{}</a>', url, obj.category.name)
        return "—"
    category_link.short_description = 'Category'
    category_link.admin_order_field = 'category__name'
    
    def status_badge(self, obj):
        """Display status as a colored badge."""
        status_colors = {
            'available': 'green',
            'in_repair': 'orange',
            'sold': 'blue',
            'scrapped': 'red',
        }
        color = status_colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 4px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def purchase_price_display(self, obj):
        """Format purchase price with currency symbol."""
        return f"${obj.purchase_price:.2f}"
    purchase_price_display.short_description = 'Purchase Price'
    purchase_price_display.admin_order_field = 'purchase_price'
    
    def characteristics_display(self, obj):
        """Display characteristics in human-readable format."""
        return obj.get_characteristics_display()
    characteristics_display.short_description = 'Characteristics Display'
    
    def is_sold_display(self, obj):
        """Display whether item is sold."""
        return obj.is_sold()
    is_sold_display.short_description = 'Is Sold?'
    is_sold_display.boolean = True
    
    def is_available_display(self, obj):
        """Display whether item is available."""
        return obj.is_available()
    is_available_display.short_description = 'Is Available?'
    is_available_display.boolean = True
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        queryset = super().get_queryset(request)
        return queryset.select_related('user', 'category')
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Customize foreign key form fields."""
        if db_field.name == "category":
            # Only show categories for the current user (if we had that filter)
            # For now, show all categories
            pass
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(InventoryItem, InventoryItemAdmin)
