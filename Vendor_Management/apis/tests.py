from django.test import TestCase
from rest_framework.test import APIClient ,APITestCase
from rest_framework import status
from django.urls import reverse
from vendor_models.models import *
from .serializers import *
from rest_framework.reverse import reverse
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
User = get_user_model()


class BuyerSignupTestCase(APITestCase):
    def test_valid_signup(self):
        """
        Test valid buyer signup.
        """
        url = reverse('buyer_signup')
        data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'password': 'testpassword',
            'confirm_password': 'testpassword',
            'address': '123 Main St',
            'contact_details': '123-456-7890'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_existing_email_signup(self):
        """
        Test signup with existing email.
        """
        # Create a user with the same email
        VendorManagementUser.objects.create_user(email='john@example.com', name='John Doe', password='testpassword')
        
        url = reverse('buyer_signup')
        data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'password': 'testpassword',
            'confirm_password': 'testpassword',
            'address': '123 Main St',
            'contact_details': '123-456-7890'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_mismatch_signup(self):
        """
        Test signup with password mismatch.
        """
        url = reverse('buyer_signup')
        data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'password': 'testpassword',
            'confirm_password': 'mismatchedpassword',
            'address': '123 Main St',
            'contact_details': '123-456-7890'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class VendorSignupTestCase(APITestCase):
    def test_valid_signup(self):
        """
        Test valid vendor signup.
        """
        url = reverse('vendor_signup')
        data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'password': 'testpassword',
            'confirm_password': 'testpassword',
            'address': '123 Main St',
            'contact_details': '123-456-7890'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_existing_email_signup(self):
        """
        Test signup with existing email.
        """
        # Create a user with the same email
        VendorManagementUser.objects.create_user(email='john@example.com', name='John Doe', password='testpassword')
        
        url = reverse('vendor_signup')
        data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'password': 'testpassword',
            'confirm_password': 'testpassword',
            'address': '123 Main St',
            'contact_details': '123-456-7890'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_mismatch_signup(self):
        """
        Test signup with password mismatch.
        """
        url = reverse('vendor_signup')
        data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'password': 'testpassword',
            'confirm_password': 'mismatchedpassword',
            'address': '123 Main St',
            'contact_details': '123-456-7890'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class VendorViewTestCase(APITestCase):
    def setUp(self):
        # Create sample VendorManagementUser instances
        user1 = VendorManagementUser.objects.create_user(email='vendor1@example.com', name='Vendor 1', password='password', address='123 Main St', contact_details='123-456-7890')
        user2 = VendorManagementUser.objects.create_user(email='vendor2@example.com', name='Vendor 2', password='password', address='456 Elm St', contact_details='987-654-3210')

        # Create sample Vendor instances related to the VendorManagementUser instances
        self.vendor1 = Vendor.objects.create(user=user1)
        self.vendor2 = Vendor.objects.create(user=user2)

    def test_list_all_vendors(self):
        """
        Test retrieving a list of all vendors.
        """
        url = reverse('vendors')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['responseData']), 2)  # Ensure both vendors are returned


class VendorDetailViewTestCase(APITestCase):
    def setUp(self):
        # Create a vendor user for testing
        self.vendor_user = VendorManagementUser.objects.create_user(email='vendor@example.com', name='Vendor', password='password', address='123 Main St', contact_details='123-456-7890')
        self.vendor = Vendor.objects.create(user=self.vendor_user)

        # Login the vendor user
        self.client = APIClient()
        self.client.force_authenticate(user=self.vendor_user)

    def test_get_vendor_detail(self):
        """
        Test retrieving details of the authenticated vendor.
        """
        url = reverse('vendor-detail')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['responseData']['name'], 'Vendor')  # Check if correct user details are returned

    def test_update_vendor_detail(self):
        """
        Test updating details of the authenticated vendor.
        """
        url = reverse('vendor-detail')
        data = {
            'name': 'Updated Vendor',
            'email': 'updated_vendor@example.com',
            'password': 'newpassword',
            'confirm_password': 'newpassword',
            'address': '456 Elm St',
            'contact_details': '987-654-3210'
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
       
    def test_delete_vendor_account(self):
        """
        Test deleting the authenticated vendor's account.
        """
        url = reverse('vendor-detail')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Check if vendor user is deleted properly
        self.assertFalse(VendorManagementUser.objects.filter(id=self.vendor.id).exists())
        # Also check if Vendor instance is deleted properly
        self.assertFalse(Vendor.objects.filter(id=self.vendor.id).exists())
    # Add more test cases as needed


class LoginViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', name='Test User', password='password', address='123 Main St', contact_details='123-456-7890')
        
    def test_login_success(self):
        url = reverse('login')
        data = {
            'email': 'test@example.com',
            'password': 'password'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data['responseData'])
        self.assertIn('refresh', response.data['responseData'])

    def test_login_invalid_credentials(self):
        url = reverse('login')
        data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data['responseData'])


