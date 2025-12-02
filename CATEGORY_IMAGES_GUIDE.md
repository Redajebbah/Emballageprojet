# Guide: Upload Category Images (Gammes)

## ✅ Setup Complete

The category model has been updated with image field support. You can now upload descriptive images for each category through the Django admin panel.

## 📋 Categories List

Your current categories:
1. **Sachet et pochette** (slug: sachet-et-pochette-2)
2. **Caisse carton et boites** (slug: caisse-carton-et-boites-0)
3. **Protection et calage** (slug: protection-et-calage-1)
4. **Stickers** (slug: stickers-5)
5. **Emballages alimentaires** (slug: emballages-alimentaires-3)
6. **Promotion** (slug: promotion-4)

## 🖼️ Recommended Image Specifications

### Image Size:
- **Dimensions**: 800x600px (4:3 ratio)
- **Minimum**: 600x450px
- **Format**: JPEG or PNG
- **File size**: Under 500KB for fast loading

### Image Style:
- Professional product photography
- Clean white or neutral background
- Good lighting showing product details
- Multiple items from the category if possible

## 📤 How to Upload Category Images

### Step 1: Access Django Admin
```
1. Open browser: http://localhost:8000/admin/
2. Login with your admin credentials
```

### Step 2: Navigate to Categories
```
1. Click on "Categories" in the left menu
2. You'll see the list of all categories
3. Each row shows: ID, Name, Slug, and Image status (✅/❌)
```

### Step 3: Edit Category
```
1. Click on the category name you want to edit
2. You'll see the edit form with these fields:
   - Name (text)
   - Slug (auto-generated, read-only)
   - Description (optional text area)
   - Image (file upload field)
```

### Step 4: Upload Image
```
1. Click "Choose File" next to the Image field
2. Select your prepared category image
3. Click "Save" at the bottom
4. The image will be uploaded to: media/categories/
```

### Step 5: Verify Display
```
1. Go to homepage: http://localhost:8000/
2. Scroll to "Explorez nos gammes d'emboitage" section
3. Your uploaded image should now display in the category card
4. Hover effect shows shadow and overlay with category name
```

## 🎨 Image Display Details

### Homepage Display:
- **Location**: "Explorez nos gammes" section (below feature boxes)
- **Size**: 180px height with auto width (responsive)
- **Style**: Rounded corners (12px), shadow, hover effects
- **Fallback**: Beige gradient if no image uploaded

### CSS Applied:
```css
.category-img {
  height: 180px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.10);
  background-size: cover;
  background-position: center;
}
```

### Template Code:
```django
{% if category.image %}
  <div class="category-img" style="background-image: url('{{ category.image.url }}');"></div>
{% else %}
  <div class="category-img" style="background: linear-gradient(...)"></div>
{% endif %}
```

## 📂 File Structure

```
backend/
  media/
    categories/          ← Images uploaded here
      sachet-pochette.jpg
      carton-boites.jpg
      protection.jpg
      stickers.jpg
      ...
  categories/
    models.py           ← Updated with image field
    admin.py            ← Enhanced admin interface
    migrations/
      0004_category_description_category_image.py  ← New migration
```

## 🔄 What's Changed

### 1. Category Model (`categories/models.py`)
```python
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=150, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)  # NEW
    image = models.ImageField(upload_to="categories/", blank=True, null=True)  # NEW
```

### 2. Category Admin (`categories/admin.py`)
```python
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'has_image')
    readonly_fields = ('slug',)
    
    def has_image(self, obj):
        return "✅" if obj.image else "❌"
```

### 3. Home View (`products/views.py`)
- Now passes `categories` to template
- Fetches all categories with image field

### 4. Home Template (`products/templates/products/home.html`)
- Dynamic category loop
- Displays uploaded images
- Fallback gradient for missing images

## 🎯 Suggested Images to Upload

### 1. Sachet et pochette
- Photo showing various plastic bags and pouches
- Bubble mailers, poly bags, zip bags

### 2. Caisse carton et boites
- Stack of different sized cardboard boxes
- Brown corrugated boxes, shipping boxes

### 3. Protection et calage
- Bubble wrap, foam sheets, packing peanuts
- Air pillows, void fill materials

### 4. Stickers
- Roll of stickers, custom labels
- Shipping labels, branding stickers

### 5. Emballages alimentaires
- Food containers, takeaway boxes
- Paper bags, food wraps

### 6. Promotion
- Special offers products
- Discounted items, bulk deals

## ✅ Testing Checklist

- [ ] Upload image for "Sachet et pochette"
- [ ] Upload image for "Caisse carton et boites"
- [ ] Upload image for "Protection et calage"
- [ ] Upload image for "Stickers"
- [ ] Verify images display on homepage
- [ ] Check hover effects work
- [ ] Test on mobile devices
- [ ] Verify category links work correctly

## 🚀 Next Steps

1. **Prepare Images**: Get professional photos for each category
2. **Upload**: Use Django admin to upload images
3. **Test**: Verify display on homepage
4. **Optimize**: Compress images if needed for faster loading

## 💡 Pro Tips

- Use consistent image style across all categories
- Optimize images before upload (compress to reduce file size)
- Use descriptive filenames (e.g., `sachet-pochette.jpg`)
- Update description field for SEO benefits
- Test on different screen sizes (mobile, tablet, desktop)

---

**All systems ready!** You can now upload category images through:
👉 http://localhost:8000/admin/categories/category/
