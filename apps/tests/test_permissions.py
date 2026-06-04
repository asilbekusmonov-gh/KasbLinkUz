# apps/test_permissions.py
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


@pytest.fixture
def worker_user():
    return User.objects.create_user(
        username='testworker',
        email='worker@test.com',
        password='Test1234!',
        role='worker',
        phone_number='902222222'
    )


@pytest.fixture
def auth_client(client_user):
    client = APIClient()
    client.force_authenticate(user=client_user)
    return client


@pytest.fixture
def auth_worker(worker_user):
    client = APIClient()
    client.force_authenticate(user=worker_user)
    return client


@pytest.mark.django_db
class TestPermissions:
    def test_unauthenticated_cannot_place_order(self, api_client):
        response = api_client.post('/api/v1/orders/', {})
        assert response.status_code == 401

    def test_unauthenticated_can_browse_services(self, api_client):
        response = api_client.get('/api/v1/services/')
        assert response.status_code == 200

    def test_unauthenticated_can_browse_categories(self, api_client):
        response = api_client.get('/api/v1/categories/')
        assert response.status_code == 200

    def test_client_cannot_create_service(self, auth_client):
        response = auth_client.post('/api/v1/services/', {
            'title': 'Test service',
            'price': 100,
        })
        assert response.status_code == 403

    def test_unauthenticated_cannot_see_orders(self, api_client):
        response = api_client.get('/api/v1/orders/')
        assert response.status_code == 401

    def test_unauthenticated_cannot_see_conversations(self, api_client):
        response = api_client.get('/api/v1/conversations/')
        assert response.status_code == 401

    def test_authenticated_can_see_own_orders(self, auth_client):
        response = auth_client.get('/api/v1/orders/')
        assert response.status_code == 200

    def test_authenticated_can_see_own_favourites(self, auth_client):
        response = auth_client.get('/api/v1/favourites/')
        assert response.status_code == 200