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
        url = reverse('order-list')
        response = api_client.post(url, {})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_unauthenticated_can_browse_services(self, api_client):
        url = reverse('service-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_unauthenticated_can_browse_categories(self, api_client):
        url = reverse('categories')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_client_cannot_create_service(self, auth_client):
        url = reverse('service-list')
        response = auth_client.post(url, {
            'title': 'Test service',
            'price': 100,
        })
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_cannot_see_orders(self, api_client):
        url = reverse('order-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_unauthenticated_cannot_see_conversations(self, api_client):
        url = reverse('conversation-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_authenticated_can_see_own_orders(self, auth_client):
        url = reverse('order-list')
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_authenticated_can_see_own_favourites(self, auth_client):
        url = reverse('favourite-list')
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK