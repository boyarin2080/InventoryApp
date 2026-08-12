from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .models import InventoryItem


class InventoryItemForm(forms.ModelForm):
    """Form for creating and updating inventory items."""
    
    class Meta:
        model = InventoryItem
        fields = [
            'category', 'name', 'description', 'purchase_date', 
            'purchase_price', 'characteristics', 'status'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter item name (e.g., iPhone 13 Pro)',
                'autofocus': True,
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter detailed description of the item',
                'rows': 4,
            }),
            'purchase_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'value': timezone.now().strftime('%Y-%m-%d'),
            }),
            'purchase_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
            }),
            'characteristics': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': '{"brand": "Apple", "model": "iPhone 13 Pro", "storage": "256GB"}',
                'rows': 6,
                'style': 'font-family: monospace;',
            }),
            'status': forms.Select(attrs={
                'class': 'form-select',
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
            }),
        }
        labels = {
            'category': _('Category'),
            'name': _('Item Name'),
            'description': _('Description'),
            'purchase_date': _('Purchase Date'),
            'purchase_price': _('Purchase Price'),
            'characteristics': _('Characteristics (JSON)'),
            'status': _('Status'),
        }
        help_texts = {
            'characteristics': _(
                'Enter JSON formatted technical specifications. '
                'Example: {"brand": "Apple", "model": "iPhone 13 Pro", "storage": "256GB"}'
            ),
            'status': _(
                'Available: Ready for sale. '
                'In Repair: Currently being repaired. '
                'Sold: Has been sold. '
                'Scrapped: No longer usable.'
            ),
        }
    
    def clean_purchase_price(self):
        """Validate that purchase price is non-negative."""
        purchase_price = self.cleaned_data.get('purchase_price')
        if purchase_price is not None and purchase_price < 0:
            raise ValidationError(_('Purchase price cannot be negative.'))
        return purchase_price
    
    def clean_characteristics(self):
        """Validate that characteristics is valid JSON."""
        characteristics = self.cleaned_data.get('characteristics')
        if characteristics:
            import json
            try:
                # Try to parse the JSON
                if isinstance(characteristics, str):
                    json.loads(characteristics)
            except (TypeError, ValueError, json.JSONDecodeError):
                raise ValidationError(_('Characteristics must be valid JSON.'))
        return characteristics
    
    def __init__(self, *args, **kwargs):
        """Initialize form and filter category choices to only show active categories."""
        super().__init__(*args, **kwargs)
        
        # Filter categories to only show active ones
        from categories.models import Category
        self.fields['category'].queryset = Category.active_categories()
