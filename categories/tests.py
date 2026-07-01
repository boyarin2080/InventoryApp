from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import Category


class CategoryModelTest(TestCase):
    """Test cases for Category model."""
    
    def setUp(self):
        """Set up test data."""
        self.root_category = Category.objects.create(
            name="Electronics",
            description="Electronic devices and components"
        )
        self.child_category = Category.objects.create(
            name="Phones",
            description="Mobile phones and smartphones",
            parent=self.root_category
        )
    
    def test_category_creation(self):
        """Test that categories can be created."""
        self.assertEqual(Category.objects.count(), 2)
        self.assertEqual(self.root_category.name, "Electronics")
        self.assertEqual(self.child_category.parent, self.root_category)
    
    def test_unique_constraint(self):
        """Test that category names must be unique within parent."""
        # Should be able to create another root category with same name
        Category.objects.create(name="Electronics", description="Another electronics category")
        
        # Should NOT be able to create another child with same parent and name
        with self.assertRaises(Exception):
            Category.objects.create(
                name="Phones", 
                description="Duplicate phone category",
                parent=self.root_category
            )
    
    def test_get_ancestors(self):
        """Test get_ancestors method."""
        grandchild = Category.objects.create(
            name="Smartphones",
            description="Smart mobile phones",
            parent=self.child_category
        )
        
        ancestors = grandchild.get_ancestors()
        self.assertEqual(len(ancestors), 2)
        self.assertIn(self.child_category, ancestors)
        self.assertIn(self.root_category, ancestors)
    
    def test_get_descendants(self):
        """Test get_descendants method."""
        descendants = self.root_category.get_descendants()
        self.assertEqual(len(descendants), 1)
        self.assertIn(self.child_category, descendants)
    
    def test_get_full_path(self):
        """Test get_full_path method."""
        grandchild = Category.objects.create(
            name="Smartphones",
            description="Smart mobile phones",
            parent=self.child_category
        )
        
        self.assertEqual(grandchild.get_full_path(), "Electronics > Phones > Smartphones")
        self.assertEqual(self.child_category.get_full_path(), "Electronics > Phones")
        self.assertEqual(self.root_category.get_full_path(), "Electronics")
    
    def test_circular_reference_prevention(self):
        """Test that circular references are prevented."""
        # Create a chain: A -> B -> C
        cat_a = Category.objects.create(name="A")
        cat_b = Category.objects.create(name="B", parent=cat_a)
        cat_c = Category.objects.create(name="C", parent=cat_b)
        
        # Try to make A parent of C (would create A->B->C->A circular reference)
        cat_a.parent = cat_c
        try:
            cat_a.full_clean()
            self.fail("Expected ValidationError for circular reference")
        except ValidationError as e:
            # Check that the error message contains the expected text
            error_messages = [str(error) for error in e.messages]
            self.assertTrue(any("circular" in msg.lower() for msg in error_messages))
    
    def test_is_root_and_level(self):
        """Test is_root and level properties."""
        self.assertTrue(self.root_category.is_root())
        self.assertFalse(self.child_category.is_root())
        self.assertEqual(self.root_category.level, 0)
        self.assertEqual(self.child_category.level, 1)
    
    def test_string_representation(self):
        """Test string representation of category."""
        self.assertEqual(str(self.root_category), "Electronics")