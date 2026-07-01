from django.test import TestCase
from django.contrib.auth import get_user_model
from categories.models import Category
from .models import InventoryItem
import json


class InventoryItemModelTest(TestCase):
    """Test cases for InventoryItem model."""
    
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
        
        # Sample JSON characteristics for testing
        self.phone_characteristics = {
            "brand": "Samsung",
            "model": "Galaxy S21",
            "storage_gb": 128,
            "ram_gb": 8,
            "color": "Phantom Black"
        }
        
        self.inventory_item = InventoryItem.objects.create(
            user=self.user,
            category=self.category,
            name="Samsung Galaxy S21",
            description="Used smartphone in good condition",
            purchase_date="2023-01-15",
            purchase_price=350.00,
            characteristics=self.phone_characteristics,
            status=InventoryItem.STATUS_AVAILABLE
        )
    
    def test_inventory_item_creation(self):
        """Test that inventory items can be created."""
        self.assertEqual(InventoryItem.objects.count(), 1)
        self.assertEqual(self.inventory_item.name, "Samsung Galaxy S21")
        self.assertEqual(self.inventory_item.user, self.user)
        self.assertEqual(self.inventory_item.category, self.category)
        self.assertEqual(self.inventory_item.purchase_price, 350.00)
        self.assertEqual(self.inventory_item.status, InventoryItem.STATUS_AVAILABLE)
    
    def test_json_characteristics(self):
        """Test JSON characteristics field."""
        self.assertEqual(self.inventory_item.characteristics, self.phone_characteristics)
        self.assertEqual(self.inventory_item.characteristics["brand"], "Samsung")
        self.assertEqual(self.inventory_item.characteristics["model"], "Galaxy S21")
        
        # Test updating JSON characteristics
        self.inventory_item.characteristics["storage_gb"] = 256
        self.inventory_item.save()
        self.inventory_item.refresh_from_db()
        self.assertEqual(self.inventory_item.characteristics["storage_gb"], 256)
    
    def test_get_characteristics_display(self):
        """Test get_characteristics_display method."""
        display = self.inventory_item.get_characteristics_display()
        self.assertIn("Brand:", display)
        self.assertIn("Samsung", display)
        self.assertIn("Model:", display)
        self.assertIn("Galaxy S21", display)
    
    def test_status_methods(self):
        """Test status-related methods."""
        # Test is_sold
        self.assertFalse(self.inventory_item.is_sold())
        
        # Test is_available
        self.assertTrue(self.inventory_item.is_available())
        
        # Test can_be_sold
        self.assertTrue(self.inventory_item.can_be_sold())
        
        # Mark as sold and retest
        self.inventory_item.mark_as_sold()
        self.assertTrue(self.inventory_item.is_sold())
        self.assertFalse(self.inventory_item.is_available())
        self.assertFalse(self.inventory_item.can_be_sold())
    
    def test_mark_as_methods(self):
        """Test mark_as_* methods."""
        # Test mark_as_in_repair
        self.inventory_item.mark_as_in_repair()
        self.assertEqual(self.inventory_item.status, InventoryItem.STATUS_IN_REPAIR)
        
        # Test mark_as_scrapped
        self.inventory_item.mark_as_scrapped()
        self.assertEqual(self.inventory_item.status, InventoryItem.STATUS_SCRAPPED)
        
        # Test mark_as_available
        self.inventory_item.mark_as_available()
        self.assertEqual(self.inventory_item.status, InventoryItem.STATUS_AVAILABLE)
    
    def test_purchase_date_properties(self):
        """Test purchase date properties."""
        self.assertEqual(self.inventory_item.purchase_year, 2023)
        self.assertEqual(self.inventory_item.purchase_month, 1)
    
    def test_validation(self):
        """Test model validation."""
        # Test negative purchase price validation
        item = InventoryItem(
            user=self.user,
            category=self.category,
            name="Test Item",
            purchase_date="2023-01-01",
            purchase_price=-100.00,
            status=InventoryItem.STATUS_AVAILABLE
        )
        
        with self.assertRaises(Exception):
            item.full_clean()
    
    def test_string_representation(self):
        """Test string representation."""
        expected_str = f"Samsung Galaxy S21 ({self.inventory_item.get_status_display()})"
        self.assertEqual(str(self.inventory_item), expected_str)