from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import Sale


class SaleAdmin(admin.ModelAdmin):
    """Admin configuration for Sale model."""
    
    list_display = (
        'inventory_item_link',
        'sale_date',
        'sale_price_display',
        'profit_display',
        'profit_margin_badge',
        'user_link',
        'created_at'
    )
    list_filter = (
        'sale_date',
        'inventory_item__category',
        'inventory_item__user',
        'created_at'
    )
    search_fields = (
        'inventory_item__name',
        'notes',
        'inventory_item__user__username',
        'inventory_item__user__email'
    )
    ordering = ('-sale_date', '-created_at')
    readonly_fields = (
        'created_at',
        'profit_display_field',
        'profit_margin_display_field',
        'is_profitable_display',
        'profit_category_display'
    )
    fieldsets = (
        ('Sale Information', {
            'fields': ('inventory_item', 'sale_date', 'sale_price', 'notes')
        }),
        ('Financial Analysis', {
            'fields': (
                'profit_display_field',
                'profit_margin_display_field',
                'is_profitable_display',
                'profit_category_display'
            )
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def inventory_item_link(self, obj):
        """Display inventory item as a clickable link."""
        if obj.inventory_item:
            url = f'/admin/inventory/inventoryitem/{obj.inventory_item.id}/change/'
            return format_html('<a href="{}">{}</a>', url, obj.inventory_item.name)
        return "—"
    inventory_item_link.short_description = 'Inventory Item'
    inventory_item_link.admin_order_field = 'inventory_item__name'
    
    def user_link(self, obj):
        """Display user as a clickable link."""
        if obj.inventory_item and obj.inventory_item.user:
            url = f'/admin/authentication/user/{obj.inventory_item.user.id}/change/'
            return format_html('<a href="{}">{}</a>', url, obj.inventory_item.user.username)
        return "—"
    user_link.short_description = 'User'
    user_link.admin_order_field = 'inventory_item__user__username'
    
    def sale_price_display(self, obj):
        """Format sale price with currency symbol."""
        return f"${obj.sale_price:.2f}"
    sale_price_display.short_description = 'Sale Price'
    sale_price_display.admin_order_field = 'sale_price'
    
    def profit_display(self, obj):
        """Display profit with colored formatting."""
        profit = obj.calculate_profit()
        color = 'green' if profit > 0 else 'red' if profit < 0 else 'gray'
        return format_html(
            '<span style="color: {}; font-weight: bold;">${:.2f}</span>',
            color,
            profit
        )
    profit_display.short_description = 'Profit'
    
    def profit_margin_badge(self, obj):
        """Display profit margin as a colored badge."""
        margin = obj.calculate_profit_margin()
        
        # Determine badge color based on margin
        if margin > 50:
            color = 'darkgreen'
            text_color = 'white'
        elif margin > 20:
            color = 'green'
            text_color = 'white'
        elif margin > 0:
            color = 'lightgreen'
            text_color = 'black'
        else:
            color = 'red'
            text_color = 'white'
        
        return format_html(
            '<span style="background-color: {}; color: {}; padding: 3px 8px; '
            'border-radius: 4px; font-weight: bold;">{:.1f}%</span>',
            color,
            text_color,
            margin
        )
    profit_margin_badge.short_description = 'Profit Margin'
    
    def profit_display_field(self, obj):
        """Display profit in read-only field."""
        return obj.get_profit_display()
    profit_display_field.short_description = 'Profit'
    
    def profit_margin_display_field(self, obj):
        """Display profit margin in read-only field."""
        return obj.get_profit_margin_display()
    profit_margin_display_field.short_description = 'Profit Margin'
    
    def is_profitable_display(self, obj):
        """Display whether sale was profitable."""
        return obj.is_profitable()
    is_profitable_display.short_description = 'Profitable?'
    is_profitable_display.boolean = True
    
    def profit_category_display(self, obj):
        """Display profit category."""
        category = obj.get_profit_category()
        category_display = {
            'high': 'High (>50%)',
            'medium': 'Medium (20-50%)',
            'low': 'Low (0-20%)',
            'loss': 'Loss'
        }.get(category, 'Unknown')
        
        colors = {
            'high': 'darkgreen',
            'medium': 'green',
            'low': 'lightgreen',
            'loss': 'red'
        }
        
        color = colors.get(category, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 4px; font-weight: bold;">{}</span>',
            color,
            category_display
        )
    profit_category_display.short_description = 'Profit Category'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        queryset = super().get_queryset(request)
        return queryset.select_related(
            'inventory_item',
            'inventory_item__user',
            'inventory_item__category'
        )
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Customize foreign key form fields."""
        if db_field.name == "inventory_item":
            # Filter to only show inventory items that are not already sold
            kwargs["queryset"] = db_field.related_model.objects.filter(
                status__in=['available', 'in_repair']
            ).select_related('user', 'category')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(Sale, SaleAdmin)
