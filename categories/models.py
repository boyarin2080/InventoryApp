from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db.models import UniqueConstraint
from django.utils import timezone


class Category(models.Model):
    """Category model for organizing inventory items with hierarchical relationships."""
    
    name = models.CharField(
        max_length=100,
        help_text=_("Category name (must be unique within parent category)")
    )
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        help_text=_("Parent category (leave empty for top-level categories)")
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Designates whether this category should be treated as active.")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("Timestamp when category was soft-deleted")
    )
    
    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ['name']
        constraints = [
            UniqueConstraint(
                fields=['name', 'parent'],
                name='unique_category_name_per_parent',
                # Null values are considered distinct in unique constraints
            )
        ]
    
    def __str__(self):
        return self.name
    
    def clean(self):
        """Validate the category before saving."""
        super().clean()
        
        # Prevent circular references
        if self.parent and self.parent.pk:
            if self.pk:  # Updating existing category
                # Check if this category is an ancestor of the parent
                ancestors = self.get_ancestors()
                if self.parent in ancestors:
                    raise ValidationError(
                        _("Cannot set a descendant category as parent (circular reference).")
                    )
        
        # Validate that category is not its own parent
        if self.pk and self.parent and self.parent.pk == self.pk:
            raise ValidationError(
                _("Category cannot be its own parent.")
            )
    
    def save(self, *args, **kwargs):
        """Override save to run full_clean before saving unless skip_validation is True."""
        skip_validation = kwargs.pop('skip_validation', False)
        if not skip_validation:
            self.full_clean()
        super().save(*args, **kwargs)
    
    def get_ancestors(self):
        """
        Get all ancestors of this category.
        
        Returns:
            list: List of Category objects representing ancestors from immediate parent to root.
        """
        ancestors = []
        parent = self.parent
        visited = set()  # Track visited nodes to prevent infinite loops
        
        while parent and parent.id not in visited:
            ancestors.append(parent)
            visited.add(parent.id)
            parent = parent.parent
            
            # Safety check to prevent infinite loops
            if len(visited) > 100:  # Arbitrary limit for safety
                break
                
        return ancestors
    
    def get_descendants(self):
        """
        Get all descendants of this category.
        
        Returns:
            list: List of Category objects representing all descendants.
        """
        descendants = []
        for child in self.children.all():
            descendants.append(child)
            descendants.extend(child.get_descendants())
        return descendants
    
    def get_full_path(self):
        """
        Get the full hierarchical path of this category.
        
        Returns:
            str: Path string like "Electronics > Computers > Laptops"
        """
        ancestors = self.get_ancestors()
        path_parts = [ancestor.name for ancestor in reversed(ancestors)]
        path_parts.append(self.name)
        return " > ".join(path_parts)
    
    def is_root(self):
        """
        Check if this is a root category (has no parent).
        
        Returns:
            bool: True if this is a root category, False otherwise.
        """
        return self.parent is None
    
    def get_root(self):
        """
        Get the root category in the hierarchy.
        
        Returns:
            Category: The root category, or self if this is a root.
        """
        if self.is_root():
            return self
        
        current = self
        while current.parent:
            current = current.parent
        return current
    
    @classmethod
    def get_root_categories(cls):
        """
        Get all root categories (categories with no parent).
        
        Returns:
            QuerySet: QuerySet of root categories.
        """
        return cls.objects.filter(parent__isnull=True)
    
    def soft_delete(self):
        """Soft delete the category by setting is_active=False and deleted_at timestamp."""
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save(skip_validation=True)
    
    def restore(self):
        """Restore a soft-deleted category."""
        self.is_active = True
        self.deleted_at = None
        self.save(skip_validation=True)
    
    @property
    def is_deleted(self):
        """Check if category is soft-deleted."""
        return not self.is_active
    
    @classmethod
    def active_categories(cls):
        """
        Get all active categories.
        
        Returns:
            QuerySet: QuerySet of active categories.
        """
        return cls.objects.filter(is_active=True)
    
    @classmethod
    def inactive_categories(cls):
        """
        Get all inactive (soft-deleted) categories.
        
        Returns:
            QuerySet: QuerySet of inactive categories.
        """
        return cls.objects.filter(is_active=False)
    
    @property
    def level(self):
        """
        Get the level in the hierarchy (0 for root, 1 for immediate children, etc.).
        
        Returns:
            int: The level in the hierarchy.
        """
        return len(self.get_ancestors())
