from django.test import TestCase, Client
from django.urls import reverse
from war.forms import RegistrationForm

class SecurityTestCase(TestCase):
    def test_clean_nim_not_numeric(self):
        form = RegistrationForm(data={
            'name': 'Test User',
            'nim': 'invalid-nim',
            'handphone': '08123456789',
            'password': 'password123',
            'confirm_password': 'password123'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('nim', form.errors)

    def test_clean_password_too_short(self):
        form = RegistrationForm(data={
            'name': 'Test User',
            'nim': '12345678',
            'handphone': '08123456789',
            'password': 'short',
            'confirm_password': 'short'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)
        
    def test_password_mismatch(self):
         form = RegistrationForm(data={
            'name': 'Test User',
            'nim': '12345678',
            'handphone': '08123456789',
            'password': 'password123',
            'confirm_password': 'password456'
        })
         self.assertFalse(form.is_valid())
         self.assertIn('confirm_password', form.errors)

    def test_api_invalid_int_input(self):
        client = Client()
        # Simulate API call with non-integer presence_id
        response = client.post(reverse('war:api_presence', args=['attend']), {
            'presence_id': 'invalid',
            'enc': 'some_encrypted_string',
            'API_KEY': 'mekbat123' # Assuming checking against default or mock setting
        })
        # We expect 400 Bad Request now, not 500
        self.assertEqual(response.status_code, 400)
