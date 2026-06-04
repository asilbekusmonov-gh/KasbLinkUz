# apps/test_auth.py
import pytest
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
        response = api_client.post('/api/v1/auth/register/', {
            'username': 'newuser',
            'email': 'new@test.com',
            'password': 'Test1234!',
            'role': 'customer',
            'phone_number': '902222222'
        })
        assert response.status_code == 201
        assert 'access' in response.data

    def test_register_missing_password(self, api_client):
        response = api_client.post('/api/v1/auth/register/', {
            'username': 'newuser',
            'email': 'new@test.com',
        })
        assert response.status_code == 400


@pytest.mark.django_db
class TestLogin:
    def test_login_success(self, api_client, client_user):
        response = api_client.post('/api/v1/auth/login/', {
            'username': 'testclient',
            'password': 'Test1234!'
        })
        assert response.status_code == 200
        assert 'access' in response.data

    def test_login_wrong_password(self, api_client, client_user):
        response = api_client.post('/api/v1/auth/login/', {
            'username': 'testclient',
            'password': 'wrongpassword'
        })
        assert response.status_code == 401