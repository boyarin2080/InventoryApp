from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from django.utils import timezone
import json


class InventoryItem(models.Model):
    """Inventory item model for tracking electronics purchased for repair and resale."""
    
    STATUS_AVAILABLE = 'available'
    STATUS_IN_REPAIR = 'in_repair'
    STATUS_SOLD = 'sold'
    STATUS_SCRAPPED = 'scrapped'
    
    STATUS_CHOICES = [
        (STATUS_AVAILABLE, _('Available')),
        (STATUS_IN_REPAIR, _('In Repair')),
        (STATUS_SOLD, _('Sold')),
        (STATUS_SCRAPPED, _('Scrapped')),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='inventory_items',
        help_text=_("User who owns this inventory item")
    )
    category = models.ForeignKey(
        'categories.Category',
        on_delete=models.SET_NULL,
        related_name='inventory_items',
        null=True,
        blank=True,
        help_text=_("Category this item belongs to")
    )
    name = models.CharField(
        max_length=200,
        help_text=_("Name or title of the inventory item")
    )
    description = models.TextField(
        blank=True,
        help_text=_("Detailed description of the item")
    )
    purchase_date = models.DateField(
        help_text=_("Date when the item was purchased")
    )
    purchase_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text=_("Purchase price in the local currency")
    )
    characteristics = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("JSON-structured technical specifications for the item")
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_AVAILABLE,
        help_text=_("Current status of the inventory item")
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("Date when the item was soft-deleted")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Inventory Item")
        verbose_name_plural = _("Inventory Items")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['user', 'category']),
            models.Index(fields=['user', 'purchase_date']),
            models.Index(fields=['status']),
            models.Index(fields=['category']),
            models.Index(fields=['purchase_date']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"
    
    def clean(self):
        """Validate the inventory item before saving."""
        super().clean()
        
        # Validate purchase price is non-negative
        if self.purchase_price < 0:
            raise ValidationError({
                'purchase_price': _("Purchase price cannot be negative.")
            })
        
        # Validate JSON characteristics
        if self.characteristics:
            try:
                # Ensure characteristics is valid JSON
                json_str = json.dumps(self.characteristics)
                json.loads(json_str)  # Validate it can be parsed
            except (TypeError, ValueError, json.JSONDecodeError):
                raise ValidationError({
                    'characteristics': _("Characteristics must be valid JSON.")
                })
        
        # Ensure the category exists
        if not self.category_id:
            raise ValidationError({
                'category': _("Category is required.")
            })
    
    def save(self, *args, **kwargs):
        """Override save to run full_clean before saving."""
        self.full_clean()
        super().save(*args, **kwargs)
    
    def is_sold(self):
        """
        Check if the item is sold.
        
        Returns:
            bool: True if status is 'sold', False otherwise.
        """
        return self.status == self.STATUS_SOLD
    
    def is_available(self):
        """
        Check if the item is available for sale.
        
        Returns:
            bool: True if status is 'available', False otherwise.
        """
        return self.status == self.STATUS_AVAILABLE
    
    def can_be_sold(self):
        """
        Check if the item can be sold.
        
        Returns:
            bool: True if item is available or in repair, False otherwise.
        """
        return self.status in [self.STATUS_AVAILABLE, self.STATUS_IN_REPAIR]
    
    def get_characteristics_display(self):
        """
        Convert JSON characteristics to human-readable HTML format.
        
        Returns:
            str: HTML-formatted string of characteristics.
        """
        if not self.characteristics:
            return _("No characteristics specified")
        
        try:
            lines = []
            for key, value in self.characteristics.items():
                # Format the key nicely (replace underscores with spaces, capitalize)
                formatted_key = key.replace('_', ' ').title()
                
                # Format the value based on type
                if isinstance(value, dict):
                    # For nested dicts, create a nested display
                    value_str = "<ul>"
                    for sub_key, sub_value in value.items():
                        formatted_sub_key = sub_key.replace('_', ' ').title()
                        value_str += f"<li><strong>{formatted_sub_key}:</strong> {sub_value}</li>"
                    value_str += "</ul>"
                elif isinstance(value, list):
                    # For lists, show as comma-separated
                    value_str = ", ".join(str(item) for item in value)
                else:
                    value_str = str(value)
                
                lines.append(f"<strong>{formatted_key}:</strong> {value_str}")
            
            return mark_safe("<br>".join(lines))
        except (AttributeError, TypeError):
            return _("Error displaying characteristics")
    
    def get_characteristics_plain_text(self):
        """
        Convert JSON characteristics to plain text format.
        
        Returns:
            str: Plain text string of characteristics.
        """
        if not self.characteristics:
            return _("No characteristics specified")
        
        try:
            lines = []
            for key, value in self.characteristics.items():
                # Format the key nicely
                formatted_key = key.replace('_', ' ').title()
                
                # Format the value based on type
                if isinstance(value, dict):
                    value_str = json.dumps(value, indent=2)
                elif isinstance(value, list):
                    value_str = ", ".join(str(item) for item in value)
                else:
                    value_str = str(value)
                
                lines.append(f"{formatted_key}: {value_str}")
            
            return "\n".join(lines)
        except (AttributeError, TypeError):
            return _("Error displaying characteristics")
    
    @property
    def purchase_year(self):
        """
        Get the year the item was purchased.
        
        Returns:
            int: Purchase year.
        """
        return self.purchase_date.year
    
    @property
    def purchase_month(self):
        """
        Get the month the item was purchased.
        
        Returns:
            int: Purchase month (1-12).
        """
        return self.purchase_date.month
    
    def mark_as_sold(self):
        """
        Mark the item as sold.
        
        Returns:
            bool: True if status was changed, False if already sold.
        """
        if self.status != self.STATUS_SOLD:
            self.status = self.STATUS_SOLD
            self.save(update_fields=['status', 'updated_at'])
            return True
        return False
    
    def mark_as_available(self):
        """
        Mark the item as available.
        
        Returns:
            bool: True if status was changed, False if already available.
        """
        if self.status != self.STATUS_AVAILABLE:
            self.status = self.STATUS_AVAILABLE
            self.save(update_fields=['status', 'updated_at'])
            return True
        return False
    
    def mark_as_in_repair(self):
        """
        Mark the item as in repair.
        
        Returns:
            bool: True if status was changed, False if already in repair.
        """
        if self.status != self.STATUS_IN_REPAIR:
            self.status = self.STATUS_IN_REPAIR
            self.save(update_fields=['status', 'updated_at'])
            return True
        return False
    
    def mark_as_scrapped(self):
        """
        Mark the item as scrapped.
        
        Returns:
            bool: True if status was changed, False if already scrapped.
        """
        if self.status != self.STATUS_SCRAPPED:
            self.status = self.STATUS_SCRAPPED
            self.save(update_fields=['status', 'updated_at'])
            return True
        return False
    
    def soft_delete(self):
        """
        Soft delete the item by setting deleted_at timestamp and nullifying related sales.
        
        Returns:
            bool: True if item was soft-deleted, False if already deleted.
        """
        if self.deleted_at is None:
            # Nullify related sales first to avoid PROTECT error
            from sales.models import Sale
            Sale.objects.filter(inventory_item=self).update(inventory_item=None)
            
            self.deleted_at = timezone.now()
            self.status = self.STATUS_SCRAPPED
            self.save(update_fields=['deleted_at', 'status', 'updated_at'])
            return True
        return False
    
    def restore(self):
        """
        Restore a soft-deleted item.
        
        Returns:
            bool: True if item was restored, False if not deleted.
        """
        if self.deleted_at is not None:
            self.deleted_at = None
            self.status = self.STATUS_AVAILABLE
            self.save(update_fields=['deleted_at', 'status', 'updated_at'])
            return True
        return False
    
    def is_deleted(self):
        """
        Check if the item is soft-deleted.
        
        Returns:
            bool: True if deleted_at is set, False otherwise.
        """
        return self.deleted_at is not None
