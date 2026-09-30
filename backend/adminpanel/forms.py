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
            'old_price',
            'category',
            'size',
            'image',
            'image2',
            'image3',
        ]
        labels = {
            'name': 'Nom',
            'price': 'Prix',
            'old_price': 'Ancien prix (promotion)',
            'category': 'Catégorie',
            'size': 'Taille',
            'image': 'Image principale',
            'image2': 'Image 2',
            'image3': 'Image 3',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'old_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'size': forms.Select(attrs={'class': 'form-select'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'image2': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'image3': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
