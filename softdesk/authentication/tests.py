from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.urls import reverse


User = get_user_model()

class UserTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password', age=20, can_be_contacted=True, can_data_be_shared=True)
        self.user_not_contacted = User.objects.create_user(username='nomailuser', password='password', age=20, can_be_contacted=False, can_data_be_shared=True)
        self.user_private = User.objects.create_user(username='privateuser', password='password', age=20, can_be_contacted=False, can_data_be_shared=False)
        self.admin_user = User.objects.create_superuser(username='admin', password='password', age=30, can_be_contacted=True, can_data_be_shared=True)
        self.token = str(RefreshToken.for_user(self.user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

    def test_get_user_list(self):
        url = reverse('user-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_get_user_not_contacted(self):
        url = reverse('user-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        for user in response.data:
            if user['username'] == 'nomailuser':
                user_data = user
                break
        self.assertIsNotNone(user_data)
        self.assertNotIn('email', user_data)
        
    def test_get_user_private_data(self):
        url = reverse('user-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        for user in response.data:
            if user['username'] == 'privateuser':
                user_private_data = user
                break
        self.assertIsNotNone(user_private_data)
        self.assertNotIn('email', user_private_data)
        self.assertNotIn('age', user_private_data)
        self.assertNotIn('can_be_contacted', user_private_data)
        
        
    def test_user_registration(self):
        url = reverse('user-list')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password123',
            'password_confirm': 'password123',
            'age': 20,
            'can_be_contacted': True,
            'can_data_be_shared': True,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_user_registration_password_mismatch(self):
        url = reverse('user-list')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password123',
            'password_confirm': 'differentpassword',
            'age': 20,
            'can_be_contacted': True,
            'can_data_be_shared': True,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(username='newuser').exists())

    def test_user_registration_invalid_age(self):
        url = reverse('user-list')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password123',
            'password_confirm': 'password123',
            'age': 14,  # Age inférieur à 15 ans
            'can_be_contacted': True,
            'can_data_be_shared': True,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(User.objects.filter(username='newuser').exists())

    def test_user_update(self):
        url = reverse('user-detail', args=[self.user.id])
        data = {
            'username': 'updateduser',
            'email': 'updateduser@example.com',
            'age': 25,
            'can_be_contacted': False,
            'can_data_be_shared': False,
        }
        response = self.client.put(url, data)
        if response.status_code != status.HTTP_200_OK:
            print(response.data)
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'updateduser')
        self.assertEqual(self.user.email, 'updateduser@example.com')
        self.assertEqual(self.user.age, 25)
        self.assertFalse(self.user.can_be_contacted)
        self.assertFalse(self.user.can_data_be_shared)

    def test_user_delete(self):
        url = reverse('user-detail', args=[self.user.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=self.user.id).exists())