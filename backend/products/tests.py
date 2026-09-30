import tempfile

from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils.text import slugify

from .models import Product
from categories.models import Category


class ProductListViewTests(TestCase):
	def setUp(self):
		self.cat1 = Category.objects.create(name='Boite carton')
		self.cat2 = Category.objects.create(name='Sachet plastique')

		# create products
		self.p1 = Product.objects.create(name='Boite 30x20', category=self.cat1, price=12.50)
		self.p2 = Product.objects.create(name='Boite 40x30', category=self.cat1, price=18.00)
		self.p3 = Product.objects.create(name='Sachet 20x20', category=self.cat2, price=0.30)

	def test_product_list_shows_all_products(self):
		url = reverse('products:product_list')
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, 200)
		# all product names should appear
		content = resp.content.decode('utf-8')
		self.assertIn(self.p1.name, content)
		self.assertIn(self.p2.name, content)
		self.assertIn(self.p3.name, content)

	def test_product_list_filter_by_category(self):
		url = reverse('products:product_list')
		cat_slug = self.cat1.slug
		resp = self.client.get(f"{url}?category={cat_slug}")
		self.assertEqual(resp.status_code, 200)
		content = resp.content.decode('utf-8')
		# only products from cat1 should appear
		self.assertIn(self.p1.name, content)
		self.assertIn(self.p2.name, content)
		self.assertNotIn(self.p3.name, content)

	def test_categories_context_contains_slug(self):
		url = reverse('products:product_list')
		resp = self.client.get(url)
		self.assertIn('categories', resp.context)
		categories = resp.context['categories']
		# categories should be a QuerySet with slug attribute
		slugs = [c.slug for c in categories]
		self.assertIn(self.cat1.slug, slugs)
		self.assertIn(self.cat2.slug, slugs)

	def test_api_product_detail(self):
		# ensures API returns the correct fields
		url = f"/api/products/{self.p1.slug}/"
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, 200)
		data = resp.json()
		expected_keys = {'id', 'name', 'slug', 'image', 'price', 'description', 'size', 'category'}
		self.assertTrue(expected_keys.issubset(set(data.keys())))
		self.assertNotIn('stock_quantity', data)
		self.assertNotIn('in_stock', data)

	def test_homepage_root(self):
		resp = self.client.get('/')
		self.assertEqual(resp.status_code, 200)
		content = resp.content.decode('utf-8')
		# home page should include the hero title text
		self.assertIn('Découvrez nos produits', content)

	def test_no_stock_or_cart_on_public_pages(self):
		for url in ['/', '/products/', f"/product/{self.p1.slug}/"]:
			content = self.client.get(url).content.decode('utf-8')
			self.assertNotIn('RUPTURE DE STOCK', content)
			self.assertNotIn('/products/cart/', content)

	def test_product_detail_has_whatsapp_quote_link(self):
		resp = self.client.get(f"/product/{self.p1.slug}/")
		self.assertEqual(resp.status_code, 200)
		content = resp.content.decode('utf-8')
		self.assertIn('https://wa.me/', content)
		self.assertIn('Demander un devis', content)


class ProductSizesTests(TestCase):
	def setUp(self):
		self.cat = Category.objects.create(name='Boîtes')
		self.product = Product.objects.create(name='Bte 10x14', category=self.cat, price=10.00)

	def test_sizes_view_empty(self):
		url = reverse('products:product_sizes', args=[self.product.id])
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, 200)
		self.assertIn('Aucune taille', resp.content.decode('utf-8'))

	def test_sizes_view_shows_sizes(self):
		# create sizes
		from .models import ProductSize
		ProductSize.objects.create(product=self.product, label='10x14', price=12.50)
		ProductSize.objects.create(product=self.product, label='14x18', price=18.00)

		url = reverse('products:product_sizes', args=[self.product.id])
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, 200)
		content = resp.content.decode('utf-8')
		self.assertIn('10x14', content)
		self.assertIn('14x18', content)
		self.assertIn('12,50', content)  # French number format

	def test_admin_product_has_sizes_inline(self):
		# import the registered ModelAdmin and ensure our inline is present
		from django.contrib import admin
		model_admin = admin.site._registry.get(Product)
		self.assertIsNotNone(model_admin)
		inline_models = [getattr(inline, 'model', None) for inline in getattr(model_admin, 'inlines', [])]
		# ProductSize model should be present in the admin inlines
		from .models import ProductSize
		self.assertIn(ProductSize, inline_models)


# Store uploads on disk during tests instead of Cloudinary.
@override_settings(
	MEDIA_ROOT=tempfile.mkdtemp(),
	STORAGES={
		'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
		'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
	},
)
class ProductImageDisplayTests(TestCase):
	def setUp(self):
		self.cat = Category.objects.create(name='AvecImage')
		self.product = Product.objects.create(name='Product with image', category=self.cat, price=5.00)

	def test_product_list_shows_image_url_when_present(self):
		# create a small in-memory image and assign to product.image
		from django.core.files.uploadedfile import SimpleUploadedFile
		img_content = (
			b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0bIDATx\x9cc``\x00\x00\x00\x04\x00\x01\x0d\n\x02\x8a\x00\x00\x00\x00IEND\xaeB`\x82"
		)

		f = SimpleUploadedFile('test.png', img_content, content_type='image/png')
		# use save() so Django storage will write the file to MEDIA_ROOT
		self.product.image.save('test-product-image.png', f, save=True)

		url = reverse('products:product_list')
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, 200)
		content = resp.content.decode('utf-8')
		# image url should appear in the rendered HTML
		# Product.image.url uses MEDIA_URL prefix, ensure substring is present
		self.assertIn(self.product.image.url, content)
