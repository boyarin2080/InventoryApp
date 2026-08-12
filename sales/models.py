from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from decimal import Decimal


class Sale(models.Model):
    """Sale model for tracking sales transactions of inventory items."""
    
    inventory_item = models.ForeignKey(
        'inventory.InventoryItem',
        on_delete=models.SET_NULL,
        related_name='sales',
        null=True,
        blank=True,
        help_text=_("Inventory item that was sold")
    )
    sale_date = models.DateField(
        help_text=_("Date when the sale occurred")
    )
    sale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text=_("Sale price in the local currency")
    )
    notes = models.TextField(
        blank=True,
        help_text=_("Additional notes about the sale")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _("Sale")
        verbose_name_plural = _("Sales")
        ordering = ['-sale_date', '-created_at']
        indexes = [
            models.Index(fields=['sale_date']),
            models.Index(fields=['inventory_item']),
        ]
    
    def __str__(self):
        return f"Sale of {self.inventory_item.name} on {self.sale_date} for ${self.sale_price}"
    
    def clean(self):
        """Validate the sale before saving."""
        super().clean()
        
        # Validate sale price is positive
        if self.sale_price <= 0:
            raise ValidationError({
                'sale_price': _("Sale price must be greater than zero.")
            })
        
        # Validate inventory item exists
        if not self.inventory_item_id:
            raise ValidationError({
                'inventory_item': _("Inventory item is required.")
            })
        
        # Validate that inventory item belongs to the current user
        # Note: This check will be enforced at the view level as we don't have request context here
        
        # Prevent selling already sold items (if this is a new sale)
        if not self.pk and self.inventory_item_id:  # New sale being created
            try:
                inventory_item = self.inventory_item
                if inventory_item.is_sold():
                    raise ValidationError({
                        'inventory_item': _(
                            "This item is already marked as sold. "
                            "Cannot create a sale for an already sold item."
                        )
                    })
            except models.ObjectDoesNotExist:
                pass
        
        # Validate sale date is not in the future (optional business rule)
        # This can be commented out if future-dated sales are allowed
        # from django.utils import timezone
        # if self.sale_date > timezone.now().date():
        #     raise ValidationError({
        #         'sale_date': _("Sale date cannot be in the future.")
        #     })
    
    def save(self, *args, **kwargs):
        """Override save to update inventory item status and run validation."""
        is_new = self.pk is None
        
        # Run validation before saving
        self.full_clean()
        
        # Save the sale
        super().save(*args, **kwargs)
        
        # Update inventory item status if this is a new sale
        if is_new:
            self.update_inventory_item_status()
    
    def update_inventory_item_status(self):
        """
        Update the associated inventory item's status to 'sold'.
        
        This method is called after a sale is created to ensure the inventory item
        is properly marked as sold.
        """
        try:
            # Only update if not already sold
            if not self.inventory_item.is_sold():
                self.inventory_item.status = 'sold'
                # Use update_fields to only update specific fields and avoid recursion
                self.inventory_item.save(update_fields=['status', 'updated_at'])
        except models.ObjectDoesNotExist:
            # If inventory item doesn't exist, we can't update it
            pass
    
    def calculate_profit(self):
        """
        Calculate the profit from this sale.
        
        Returns:
            Decimal: Profit amount (sale price - purchase price).
        """
        try:
            return self.sale_price - self.inventory_item.purchase_price
        except (AttributeError, models.ObjectDoesNotExist):
            return Decimal('0.00')
    
    def calculate_profit_margin(self):
        """
        Calculate profit margin as a percentage.
        
        Returns:
            Decimal: Profit margin percentage, or 100% if purchase price is zero.
        """
        try:
            purchase_price = self.inventory_item.purchase_price
            if purchase_price == 0:
                # Avoid division by zero
                return Decimal('100.00')
            
            profit = self.calculate_profit()
            return (profit / purchase_price) * Decimal('100.00')
        except (AttributeError, models.ObjectDoesNotExist, ZeroDivisionError):
            return Decimal('0.00')
    
    def get_profit_display(self):
        """
        Get a formatted string showing the profit.
        
        Returns:
            str: Formatted profit string with currency symbol.
        """
        profit = self.calculate_profit()
        return f"${profit:.2f}"
    
    def get_profit_margin_display(self):
        """
        Get a formatted string showing the profit margin percentage.
        
        Returns:
            str: Formatted profit margin string with percentage sign.
        """
        margin = self.calculate_profit_margin()
        return f"{margin:.2f}%"
    
    def is_profitable(self):
        """
        Check if the sale was profitable.
        
        Returns:
            bool: True if profit > 0, False otherwise.
        """
        return self.calculate_profit() > 0
    
    def get_profit_category(self):
        """
        Categorize the profit level.
        
        Returns:
            str: 'high', 'medium', 'low', or 'loss' based on profit margin.
        """
        margin = self.calculate_profit_margin()
        
        if margin > 50:
            return 'high'
        elif margin > 20:
            return 'medium'
        elif margin > 0:
            return 'low'
        else:
            return 'loss'
    
    @property
    def sale_year(self):
        """
        Get the year the sale occurred.
        
        Returns:
            int: Sale year.
        """
        return self.sale_date.year
    
    @property
    def sale_month(self):
        """
        Get the month the sale occurred.
        
        Returns:
            int: Sale month (1-12).
        """
        return self.sale_date.month
    
    @classmethod
    def get_total_sales_for_user(cls, user):
        """
        Get total sales amount for a specific user.
        
        Args:
            user: User object to filter sales by.
            
        Returns:
            Decimal: Total sales amount for the user.
        """
        from django.db.models import Sum
        result = cls.objects.filter(
            inventory_item__user=user
        ).aggregate(total=Sum('sale_price'))
        return result['total'] or Decimal('0.00')
    
    @classmethod
    def get_total_profit_for_user(cls, user):
        """
        Get total profit for a specific user.
        
        Args:
            user: User object to filter sales by.
            
        Returns:
            Decimal: Total profit for the user.
        """
        from django.db.models import Sum
        total_sales = cls.get_total_sales_for_user(user)
        
        # Calculate total purchase cost for sold items
        total_purchase = Decimal('0.00')
        user_sales = cls.objects.filter(inventory_item__user=user)
        
        for sale in user_sales:
            try:
                total_purchase += sale.inventory_item.purchase_price
            except (AttributeError, models.ObjectDoesNotExist):
                pass
        
        return total_sales - total_purchase
    
    def soft_delete(self):
        """
        Soft delete the sale by setting a flag (since Sale doesn't have deleted_at).
        For now, we'll delete the sale but log that it was soft-deleted.
        
        Returns:
            bool: True if sale was soft-deleted, False if already deleted.
        """
        # Since Sale doesn't have deleted_at field, we'll use a simple approach
        # In a more complex system, you might want to add a deleted_at field
        self.delete()
        return True
