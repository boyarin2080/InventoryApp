from django.contrib import admin
from django.utils.html import format_html
from .models import Category


class CategoryAdmin(admin.ModelAdmin):
    """Admin configuration for Category model."""
    
    list_display = ('name', 'parent_link', 'item_count', 'level', 'created_at')
    list_filter = ('parent', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('parent__name', 'name')
    readonly_fields = ('created_at', 'updated_at', 'level_display', 'full_path')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'parent')
        }),
        ('Hierarchy Information', {
            'fields': ('level_display', 'full_path', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def parent_link(self, obj):
        """Display parent as a clickable link."""
        if obj.parent:
            url = f'/admin/categories/category/{obj.parent.id}/change/'
            return format_html('<a href="{}">{}</a>', url, obj.parent.name)
        return "—"
    parent_link.short_description = 'Parent'
    parent_link.admin_order_field = 'parent__name'
    
    def item_count(self, obj):
        """Display count of inventory items in this category."""
        return obj.inventory_items.count()
    item_count.short_description = 'Items'
    
    def level_display(self, obj):
        """Display the hierarchy level."""
        return obj.level
    level_display.short_description = 'Level'
    
    def full_path(self, obj):
        """Display the full hierarchical path."""
        return obj.get_full_path()
    full_path.short_description = 'Full Path'
    
    def get_queryset(self, request):
        """Optimize queryset with prefetch_related."""
        queryset = super().get_queryset(request)
        return queryset.select_related('parent').prefetch_related('inventory_items')


admin.site.register(Category, CategoryAdmin)
