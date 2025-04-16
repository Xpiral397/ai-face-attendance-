import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from mixer.backend.django import mixer
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_user():
    def _create_user(username='testuser', password='testpassword', role=User.Role.STUDENT):
        return User.objects.create_user(
            username=username,
            email=f'{username}@example.com',
            password=password,
            role=role
        )
    return _create_user

@pytest.mark.django_db
class TestAuthEndpoints:
    def test_register(self, api_client):
        """Test user registration"""
        url = reverse('auth-register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'securepassword',
            'full_name': 'New User',
            'role': User.Role.STUDENT
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert 'user' in response.data
        
        # Check user was created
        assert User.objects.filter(username='newuser').exists()
    
    def test_login(self, api_client, create_user):
        """Test user login"""
        user = create_user()
        url = reverse('auth-login')
        data = {
            'username': 'testuser',
            'password': 'testpassword'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert 'user' in response.data
    
    def test_invalid_login(self, api_client, create_user):
        """Test login with invalid credentials"""
        user = create_user()
        url = reverse('auth-login')
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_profile(self, api_client, create_user):
        """Test getting user profile"""
        user = create_user()
        url = reverse('auth-profile')
        
        # Get token
        login_url = reverse('auth-login')
        login_data = {
            'username': 'testuser',
            'password': 'testpassword'
        }
        login_response = api_client.post(login_url, login_data, format='json')
        token = login_response.data['access']
        
        # Request profile with token
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == 'testuser'
        assert response.data['email'] == 'testuser@example.com'
    
    def test_unauthorized_profile(self, api_client):
        """Test getting profile without authentication"""
        url = reverse('auth-profile')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED 