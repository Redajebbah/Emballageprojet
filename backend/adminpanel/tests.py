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
