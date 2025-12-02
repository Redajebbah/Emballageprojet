from django.test import TestCase
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
		url = reverse('product_list')
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, 200)
		# all product names should appear
		content = resp.content.decode('utf-8')
		self.assertIn(self.p1.name, content)
		self.assertIn(self.p2.name, content)
		self.assertIn(self.p3.name, content)

	def test_product_list_filter_by_category(self):
		url = reverse('product_list')
		cat_slug = self.cat1.slug
		resp = self.client.get(f"{url}?category={cat_slug}")
		self.assertEqual(resp.status_code, 200)
		content = resp.content.decode('utf-8')
		# only products from cat1 should appear
		self.assertIn(self.p1.name, content)
		self.assertIn(self.p2.name, content)
		self.assertNotIn(self.p3.name, content)

	def test_categories_context_contains_slug(self):
		url = reverse('product_list')
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
		expected_keys = {'id', 'name', 'slug', 'image', 'price', 'description', 'size', 'stock_quantity', 'in_stock', 'category'}
		self.assertTrue(expected_keys.issubset(set(data.keys())))

	def test_homepage_root(self):
		resp = self.client.get('/')
		self.assertEqual(resp.status_code, 200)
		content = resp.content.decode('utf-8')
		# home page should include the hero title text
		self.assertIn('Matériel d\'emballage professionnel', content)

	def test_cart_add_and_detail(self):
		cart_url = reverse('products:cart_add')
		detail_url = reverse('products:cart_detail')
		# add p1 to cart
		resp = self.client.post(cart_url, {'slug': self.p1.slug, 'quantity': 2})
		# should redirect to cart_detail
		self.assertEqual(resp.status_code, 302)

		# now view cart
		resp = self.client.get(detail_url)
		self.assertEqual(resp.status_code, 200)
		content = resp.content.decode('utf-8')
		self.assertIn(self.p1.name, content)
		self.assertIn('2', content)

	def test_cart_update_remove_clear(self):
		# add then update then remove then clear
		cart_url = reverse('products:cart_add')
		detail_url = reverse('products:cart_detail')
		update_url = reverse('products:cart_update')
		remove_url = reverse('products:cart_remove')
		clear_url = reverse('products:cart_clear')

		self.client.post(cart_url, {'slug': self.p1.slug, 'quantity': 1})
		self.client.post(cart_url, {'slug': self.p2.slug, 'quantity': 1})
		resp = self.client.get(detail_url)
		self.assertEqual(resp.status_code, 200)

		# update quantity of p1 to 3
		self.client.post(update_url, {'product_id': str(self.p1.id), 'quantity': 3})
		resp = self.client.get(detail_url)
		self.assertIn('3', resp.content.decode('utf-8'))

		# remove p2
		self.client.post(remove_url, {'product_id': str(self.p2.id)})
		resp = self.client.get(detail_url)
		self.assertNotIn(self.p2.name, resp.content.decode('utf-8'))

		# clear
		self.client.post(clear_url)
		resp = self.client.get(detail_url)
		self.assertIn('Votre panier est vide', resp.content.decode('utf-8'))


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
		ProductSize.objects.create(product=self.product, label='10x14', price=12.50, stock=10)
		ProductSize.objects.create(product=self.product, label='14x18', price=18.00, stock=5)

		url = reverse('products:product_sizes', args=[self.product.id])
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, 200)
		content = resp.content.decode('utf-8')
		self.assertIn('10x14', content)
		self.assertIn('14x18', content)
		self.assertIn('12.5', content)  # price formatting might show 12.50

	def test_admin_product_has_sizes_inline(self):
		# import the registered ModelAdmin and ensure our inline is present
		from django.contrib import admin
		model_admin = admin.site._registry.get(Product)
		self.assertIsNotNone(model_admin)
		inline_models = [getattr(inline, 'model', None) for inline in getattr(model_admin, 'inlines', [])]
		# ProductSize model should be present in the admin inlines
		from .models import ProductSize
		self.assertIn(ProductSize, inline_models)


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

		url = reverse('product_list')
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, 200)
		content = resp.content.decode('utf-8')
		# image url should appear in the rendered HTML
		# Product.image.url uses MEDIA_URL prefix, ensure substring is present
		self.assertIn(self.product.image.url, content)
