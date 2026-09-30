from django.test import TestCase
from django.urls import reverse


class AdminPanelViewsTests(TestCase):

    def test_login_get(self):
        url = reverse('adminpanel:login')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        # login page should render a form (csrf token + password input)
        self.assertContains(resp, 'csrfmiddlewaretoken')
        self.assertContains(resp, 'name="password"')

    def test_dashboard_requires_login(self):
        url = reverse('adminpanel:dashboard')
        resp = self.client.get(url)
        # should redirect to login when not authenticated
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/admin-panel/login/', resp.url)


import shutil
import tempfile

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings

from categories.models import Category
from products.models import Product, ProductSize

TEST_MEDIA = tempfile.mkdtemp()
def make_png():
    """A real (valid) 2x2 PNG, generated with Pillow."""
    import io
    from PIL import Image
    buf = io.BytesIO()
    Image.new('RGB', (2, 2), (200, 160, 100)).save(buf, format='PNG')
    return buf.getvalue()


PNG = make_png()


def sizes_management(total=3, initial=0):
    return {
        'sizes-TOTAL_FORMS': str(total), 'sizes-INITIAL_FORMS': str(initial),
        'sizes-MIN_NUM_FORMS': '0', 'sizes-MAX_NUM_FORMS': '1000',
    }


# Store uploads on disk during tests instead of Cloudinary.
@override_settings(
    MEDIA_ROOT=TEST_MEDIA,
    STORAGES={
        'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
        'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
    },
)
class AdminPanelProductCrudTests(TestCase):

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEST_MEDIA, ignore_errors=True)

    def setUp(self):
        User.objects.create_superuser('boss', 'boss@example.test', 'pass-1234')
        self.cat = Category.objects.create(name='Caisse carton')
        resp = self.client.post(reverse('adminpanel:login'), {'email': 'boss@example.test', 'password': 'pass-1234'})
        self.assertRedirects(resp, reverse('adminpanel:dashboard'))

    def test_pages_render(self):
        for name in ['dashboard', 'products_list', 'products_add']:
            resp = self.client.get(reverse(f'adminpanel:{name}'))
            self.assertEqual(resp.status_code, 200, name)
        resp = self.client.get(reverse('adminpanel:dashboard'))
        self.assertContains(resp, '/admin/categories/category/')

    def test_add_edit_delete_product_with_image_and_sizes(self):
        data = {
            'name': 'Boite 40x30', 'description': 'Solide', 'price': '8.00', 'old_price': '10.00',
            'category': self.cat.pk, 'size': '',
            'image': SimpleUploadedFile('boite.png', PNG, content_type='image/png'),
            **sizes_management(),
            'sizes-0-label': '40x30', 'sizes-0-price': '8.00',
            'sizes-1-label': '50x40', 'sizes-1-price': '11.50',
        }
        resp = self.client.post(reverse('adminpanel:products_add'), data)
        self.assertRedirects(resp, reverse('adminpanel:products_list'))
        prod = Product.objects.get(name='Boite 40x30')
        self.assertTrue(prod.image.name.startswith('products/boite'))
        self.assertEqual(prod.old_price, 10)
        self.assertEqual(sorted(prod.sizes.values_list('label', flat=True)), ['40x30', '50x40'])

        # the photo and the sizes show up on the public product page
        page = self.client.get(f'/product/{prod.slug}/').content.decode()
        self.assertIn(prod.image.url, page)
        self.assertIn('50x40', page)

        # edit: change price, drop one size, keep the image
        size_40, size_50 = prod.sizes.order_by('label')
        data = {
            'name': 'Boite 40x30', 'description': 'Solide', 'price': '7.50', 'old_price': '',
            'category': self.cat.pk, 'size': '',
            **sizes_management(total=5, initial=2),
            'sizes-0-id': size_40.pk, 'sizes-0-label': '40x30', 'sizes-0-price': '7.50',
            'sizes-1-id': size_50.pk, 'sizes-1-label': '50x40', 'sizes-1-price': '11.50', 'sizes-1-DELETE': 'on',
        }
        resp = self.client.post(reverse('adminpanel:products_edit', args=[prod.pk]), data)
        self.assertRedirects(resp, reverse('adminpanel:products_list'))
        prod.refresh_from_db()
        self.assertEqual(str(prod.price), '7.50')
        self.assertIsNone(prod.old_price)
        self.assertTrue(prod.image)
        self.assertEqual(list(prod.sizes.values_list('label', flat=True)), ['40x30'])

        # the edit page renders with current images
        resp = self.client.get(reverse('adminpanel:products_edit', args=[prod.pk]))
        self.assertContains(resp, 'Images actuelles')

        # delete
        resp = self.client.post(reverse('adminpanel:products_delete', args=[prod.pk]))
        self.assertRedirects(resp, reverse('adminpanel:products_list'))
        self.assertFalse(Product.objects.filter(pk=prod.pk).exists())
        self.assertFalse(ProductSize.objects.filter(label='40x30').exists())

    def test_invalid_product_shows_errors(self):
        resp = self.client.post(reverse('adminpanel:products_add'), {'name': '', 'price': '', **sizes_management()})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Product.objects.count(), 0)

    def test_category_can_be_edited_with_image_in_django_admin(self):
        resp = self.client.post(f'/admin/categories/category/{self.cat.pk}/change/', {
            'name': 'Caisse carton', 'description': 'Cartons',
            'image': SimpleUploadedFile('cat.png', PNG, content_type='image/png'),
        })
        self.assertEqual(resp.status_code, 302)
        self.cat.refresh_from_db()
        self.assertTrue(self.cat.image.name.startswith('categories/cat'))
