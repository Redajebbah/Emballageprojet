from django import forms
from products.models import Product
from categories.models import Category
from .models import ProductImage
from django.forms.widgets import ClearableFileInput


# ---------------------------
# Custom widget for multiple images
# ---------------------------
class MultipleFileInput(ClearableFileInput):
    allow_multiple_selected = True


# ---------------------------
# Admin Login Form
# ---------------------------
class AdminLoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Admin email'
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Password'
            }
        )
    )


# ---------------------------
# Add / Edit Product Form
# ---------------------------
class ProductForm(forms.ModelForm):
    # Multiple image upload support (Django 5 compliant)
    images = forms.FileField(
        widget=MultipleFileInput(),
        required=False
    )

    class Meta:
        model = Product
        fields = [
            'name',
            'description',
            'price',
            'category',
            'size',
            'stock_quantity',
            'in_stock'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'size': forms.TextInput(attrs={'class': 'form-control'}),
            'stock_quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'in_stock': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


# ---------------------------
# Stock Update Form
# ---------------------------
class StockUpdateForm(forms.Form):
    product_id = forms.IntegerField(widget=forms.HiddenInput())
    stock = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'min': 0
            }
        )
    )
