import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.models import User


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def client_user():
    return User.objects.create_user(
        username='testclient',
        email='client@test.com',
        password='Test1234!',
        role='customer',
        phone_number='901111111'
    )


@pytest.mark.django_db
class TestRegister:
    def test_register_success(self, api_client):
        url = reverse('register')  # name from path('auth/register/', RegisterView.as_view(), name='register')
        response = api_client.post(url, {
            'username': 'newuser',
            'email': 'new@test.com',
            'password': 'Test1234!',
            'role': 'customer',
            'phone_number': '902222222'
        })
        assert response.status_code == status.HTTP_201_CREATED
        assert 'access' in response.data

    def test_register_missing_password(self, api_client):
        url = reverse('register')
        response = api_client.post(url, {
            'username': 'newuser',
            'email': 'new@test.com',
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestLogin:
    def test_login_success(self, api_client, client_user):
        url = reverse('token_obtain_pair')  # name from path('auth/login/', ..., name='token_obtain_pair')
        response = api_client.post(url, {
            'username': 'testclient',
            'password': 'Test1234!'
        })
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data

    def test_login_wrong_password(self, api_client, client_user):
        url = reverse('token_obtain_pair')
        response = api_client.post(url, {
            'username': 'testclient',
            'password': 'wrongpassword'
        })
        assert response.status_code == status.HTTP_401_UNAUTHORIZED