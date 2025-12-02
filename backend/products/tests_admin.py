from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse


class ProductAdminTests(TestCase):
    def setUp(self):
        # create a superuser
        self.admin = User.objects.create_superuser('admin2', 'admin2@example.com', 'pass1234')

    def test_admin_product_changelist(self):
        # login to admin and access product changelist
        login = self.client.login(username='admin2', password='pass1234')
        self.assertTrue(login)

        url = '/admin/products/product/'
        resp = self.client.get(url)
        # should return 200 even if no products exist
        self.assertEqual(resp.status_code, 200)
