from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import Category


class CategoryForm(forms.ModelForm):
    """Form for creating and updating categories."""
    
    class Meta:
        model = Category
        fields = ['name', 'description', 'parent']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter category name',
                'autofocus': True,
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter category description (optional)',
                'rows': 4,
            }),
            'parent': forms.Select(attrs={
                'class': 'form-select',
            }),
        }
        labels = {
            'parent': _('Parent Category (optional)'),
        }
        help_texts = {
            'name': _('Category name must be unique within the same parent category.'),
            'parent': _('Select a parent category to create a sub-category. Leave empty for a top-level category.'),
        }
    
    def __init__(self, *args, **kwargs):
        """Initialize form with custom parent queryset."""
        super().__init__(*args, **kwargs)
        
        # Get instance if editing existing category
        instance = kwargs.get('instance')
        
        # Filter parent choices to avoid circular references
        if instance and instance.pk:
            # Exclude self and descendants from parent choices
            descendants = instance.get_descendants()
            exclude_ids = [descendant.id for descendant in descendants]
            exclude_ids.append(instance.id)
            
            self.fields['parent'].queryset = Category.objects.exclude(
                id__in=exclude_ids
            )
        else:
            # For new categories, all categories are valid parents
            self.fields['parent'].queryset = Category.objects.all()
        
        # Add "No parent" option
        self.fields['parent'].empty_label = "--- No parent (top-level category) ---"
    
    def clean(self):
        """Validate form data."""
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        parent = cleaned_data.get('parent')
        
        # Check for uniqueness within parent
        if name and parent:
            # Check if a category with same name and parent already exists
            existing = Category.objects.filter(
                name=name,
                parent=parent
            )
            
            # Exclude current instance if editing
            if self.instance and self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise ValidationError(
                    _('A category with this name already exists under the selected parent.')
                )
        elif name:
            # Check for root category uniqueness
            existing = Category.objects.filter(
                name=name,
                parent__isnull=True
            )
            
            # Exclude current instance if editing
            if self.instance and self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise ValidationError(
                    _('A root category with this name already exists.')
                )
        
        return cleaned_data
    
    def clean_parent(self):
        """Validate parent field."""
        parent = self.cleaned_data.get('parent')
        
        # If editing existing category, prevent circular references
        if self.instance and self.instance.pk and parent:
            # Check if parent is a descendant of this category
            descendants = self.instance.get_descendants()
            if parent in descendants:
                raise ValidationError(
                    _('Cannot set a descendant category as parent (circular reference).')
                )
            
            # Check if parent is self
            if parent.id == self.instance.id:
                raise ValidationError(
                    _('Category cannot be its own parent.')
                )
        
        return parent