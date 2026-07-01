from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from decimal import Decimal
from categories.models import Category
from inventory.models import InventoryItem
from .models import Sale


class SaleModelTest(TestCase):
    """Test cases for Sale model."""
    
    def setUp(self):
        """Set up test data."""
        User = get_user_model()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        
        self.category = Category.objects.create(
            name="Electronics",
            description="Electronic devices"
        )
        
        self.inventory_item = InventoryItem.objects.create(
            user=self.user,
            category=self.category,
            name="Samsung Galaxy S21",
            description="Used smartphone in good condition",
            purchase_date="2023-01-15",
            purchase_price=350.00,
            characteristics={"brand": "Samsung", "model": "Galaxy S21"},
            status=InventoryItem.STATUS_AVAILABLE
        )
        
        self.sale = Sale.objects.create(
            inventory_item=self.inventory_item,
            sale_date="2023-02-20",
            sale_price=450.00,
            notes="Sold to regular customer"
        )
    
    def test_sale_creation(self):
        """Test that sales can be created."""
        self.assertEqual(Sale.objects.count(), 1)
        self.assertEqual(self.sale.inventory_item, self.inventory_item)
        self.assertEqual(self.sale.sale_date.year, 2023)
        self.assertEqual(self.sale.sale_date.month, 2)
        self.assertEqual(self.sale.sale_price, Decimal('450.00'))
        self.assertEqual(self.sale.notes, "Sold to regular customer")
    
    def test_inventory_status_update(self):
        """Test that sale creation updates inventory item status."""
        # The inventory item should now be marked as sold
        self.inventory_item.refresh_from_db()
        self.assertEqual(self.inventory_item.status, InventoryItem.STATUS_SOLD)
        self.assertTrue(self.inventory_item.is_sold())
    
    def test_calculate_profit(self):
        """Test profit calculation."""
        profit = self.sale.calculate_profit()
        self.assertEqual(profit, Decimal('100.00'))  # 450 - 350 = 100
    
    def test_calculate_profit_margin(self):
        """Test profit margin calculation."""
        margin = self.sale.calculate_profit_margin()
        # (100 / 350) * 100 = 28.57%
        expected_margin = (Decimal('100.00') / Decimal('350.00')) * Decimal('100.00')
        self.assertAlmostEqual(float(margin), float(expected_margin), places=2)
    
    def test_profit_methods_with_zero_purchase_price(self):
        """Test profit methods with zero purchase price."""
        # Create an item with zero purchase price
        free_item = InventoryItem.objects.create(
            user=self.user,
            category=self.category,
            name="Free Item",
            purchase_date="2023-01-01",
            purchase_price=0.00,
            status=InventoryItem.STATUS_AVAILABLE
        )
        
        sale = Sale.objects.create(
            inventory_item=free_item,
            sale_date="2023-02-01",
            sale_price=100.00
        )
        
        # Profit should be 100 (100 - 0)
        self.assertEqual(sale.calculate_profit(), Decimal('100.00'))
        
        # Profit margin should be 100% (division by zero protection)
        self.assertEqual(sale.calculate_profit_margin(), Decimal('100.00'))
    
    def test_validation_positive_sale_price(self):
        """Test that sale price must be positive."""
        sale = Sale(
            inventory_item=self.inventory_item,
            sale_date="2023-02-20",
            sale_price=0.00,  # Zero price
            notes="Test sale"
        )
        
        with self.assertRaises(ValidationError):
            sale.full_clean()
    
    def test_prevent_sale_of_already_sold_item(self):
        """Test that already sold items cannot be sold again."""
        # Try to create another sale for the same item
        with self.assertRaises(ValidationError):
            duplicate_sale = Sale(
                inventory_item=self.inventory_item,
                sale_date="2023-02-21",
                sale_price=500.00
            )
            duplicate_sale.full_clean()
    
    def test_get_profit_display(self):
        """Test get_profit_display method."""
        profit_display = self.sale.get_profit_display()
        self.assertEqual(profit_display, "$100.00")
    
    def test_get_profit_margin_display(self):
        """Test get_profit_margin_display method."""
        margin_display = self.sale.get_profit_margin_display()
        self.assertEqual(margin_display, "28.57%")
    
    def test_is_profitable(self):
        """Test is_profitable method."""
        self.assertTrue(self.sale.is_profitable())
        
        # Create a sale with loss
        loss_item = InventoryItem.objects.create(
            user=self.user,
            category=self.category,
            name="Loss Item",
            purchase_date="2023-01-01",
            purchase_price=500.00,
            status=InventoryItem.STATUS_AVAILABLE
        )
        
        loss_sale = Sale.objects.create(
            inventory_item=loss_item,
            sale_date="2023-02-01",
            sale_price=400.00  # Sold for less than purchase price
        )
        
        self.assertFalse(loss_sale.is_profitable())
    
    def test_sale_date_properties(self):
        """Test sale date properties."""
        self.assertEqual(self.sale.sale_year, 2023)
        self.assertEqual(self.sale.sale_month, 2)
    
    def test_string_representation(self):
        """Test string representation."""
        expected_str = f"Sale of {self.inventory_item.name} on {self.sale.sale_date} for ${self.sale.sale_price}"
        self.assertEqual(str(self.sale), expected_str)