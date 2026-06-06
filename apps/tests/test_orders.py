import datetime

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.models import User, WorkerProfile, Category, Service


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
def worker_profile(worker_user):
    return WorkerProfile.objects.create(
        user=worker_user,
        bio='Test bio',
        rating=0,
        completed_orders_count=0,
        work_start_time=timezone.make_aware(datetime.datetime(2026, 1, 1, 9, 0)),
        work_end_time=timezone.make_aware(datetime.datetime(2026, 1, 1, 18, 0)),
    )


@pytest.fixture
def category():
    return Category.objects.create(name='Test Category')


@pytest.fixture
def service(worker_profile, category):
    return Service.objects.create(
        worker=worker_profile,
        category=category,
        name='Test Service',
        min_price=100,
        max_price=200,
        description='Test description'
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
class TestOrders:
    def test_client_can_place_order(self, auth_client, service, worker_profile):
        url = reverse('order-list')
        response = auth_client.post(url, {
            'title': 'Fix my sink',
            'description': 'Need a plumber',
            'address': 'Tashkent, Chilonzor',
            'service': service.id,
            'worker': worker_profile.id,
        })
        assert response.status_code == status.HTTP_201_CREATED

    def test_order_starts_as_pending(self, auth_client, service, worker_profile):
        url = reverse('order-list')
        response = auth_client.post(url, {
            'title': 'Fix my sink',
            'description': 'Need a plumber',
            'address': 'Tashkent, Chilonzor',
            'service': service.id,
            'worker': worker_profile.id,
        })
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['status'] == 'pending'

    def test_unauthenticated_cannot_place_order(self, api_client, service):
        url = reverse('order-list')
        response = api_client.post(url, {
            'service': service.id,
        })
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_worker_can_accept_order(self, auth_client, auth_worker, service, worker_profile):
        # Client places order
        order_response = auth_client.post(reverse('order-list'), {
            'title': 'Fix my sink',
            'description': 'Need a plumber',
            'address': 'Tashkent, Chilonzor',
            'service': service.id,
            'worker': worker_profile.id,
        })
        assert order_response.status_code == status.HTTP_201_CREATED
        order_id = order_response.data['id']

        # Worker accepts it
        url = reverse('order-accepted', args=[order_id])
        response = auth_worker.patch(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'accepted'

    def test_cannot_cancel_completed_order(self, auth_client, auth_worker, service, worker_profile):
        # Place order
        order_response = auth_client.post(reverse('order-list'), {
            'title': 'Fix my sink',
            'description': 'Need a plumber',
            'address': 'Tashkent, Chilonzor',
            'service': service.id,
            'worker': worker_profile.id,
        })
        assert order_response.status_code == status.HTTP_201_CREATED
        order_id = order_response.data['id']

        # Worker accepts
        accept_response = auth_worker.patch(reverse('order-accepted', args=[order_id]))
        assert accept_response.status_code == status.HTTP_200_OK

        # Worker completes
        complete_response = auth_worker.patch(reverse('order-completed', args=[order_id]))
        assert complete_response.status_code == status.HTTP_200_OK

        # Client tries to cancel — should fail
        response = auth_client.patch(reverse('order-cancelled', args=[order_id]))
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_client_can_see_own_orders(self, auth_client, service, worker_profile):
        # Create order first
        auth_client.post(reverse('order-list'), {
            'title': 'Fix my sink',
            'description': 'Need a plumber',
            'address': 'Tashkent, Chilonzor',
            'service': service.id,
            'worker': worker_profile.id,
        })
        # List orders
        response = auth_client.get(reverse('order-list'))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) > 0

    def test_client_can_retrieve_own_order(self, auth_client, service, worker_profile):
        order_response = auth_client.post(reverse('order-list'), {
            'title': 'Fix my sink',
            'description': 'Need a plumber',
            'address': 'Tashkent, Chilonzor',
            'service': service.id,
            'worker': worker_profile.id,
        })
        order_id = order_response.data['id']

        url = reverse('order-detail', args=[order_id])
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == order_id

    def test_order_cannot_be_deleted(self, auth_client, service, worker_profile):
        order_response = auth_client.post(reverse('order-list'), {
            'title': 'Fix my sink',
            'description': 'Need a plumber',
            'address': 'Tashkent, Chilonzor',
            'service': service.id,
            'worker': worker_profile.id,
        })
        order_id = order_response.data['id']

        url = reverse('order-detail', args=[order_id])
        response = auth_client.delete(url)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_client_can_cancel_pending_order(self, auth_client, service, worker_profile):
        order_response = auth_client.post(reverse('order-list'), {
            'title': 'Fix my sink',
            'description': 'Need a plumber',
            'address': 'Tashkent, Chilonzor',
            'service': service.id,
            'worker': worker_profile.id,
        })
        order_id = order_response.data['id']

        url = reverse('order-cancelled', args=[order_id])
        response = auth_client.patch(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'cancelled'
