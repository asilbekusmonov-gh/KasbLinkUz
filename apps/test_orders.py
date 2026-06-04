import pytest
from rest_framework.test import APIClient
from apps.models import User, WorkerProfile, Category, Service
from django.utils import timezone
import datetime

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
        response = auth_client.post('/api/v1/orders/', {
            'title': 'Fix my sink',
            'description': 'Need a plumber',
            'address': 'Tashkent, Chilonzor',
            'service': service.id,
            'worker': worker_profile.id,
        })
        assert response.status_code == 201

    def test_order_starts_as_pending(self, auth_client, service, worker_profile):
        response = auth_client.post('/api/v1/orders/', {
            'title': 'Fix my sink',
            'description': 'Need a plumber',
            'address': 'Tashkent, Chilonzor',
            'service': service.id,
            'worker': worker_profile.id,
        })
        assert response.status_code == 201
        assert response.data['status'] == 'pending'

    def test_unauthenticated_cannot_place_order(self, api_client, service):
        response = api_client.post('/api/v1/orders/', {
            'service': service.id,
        })
        assert response.status_code == 401

    def test_worker_can_accept_order(self, auth_client, auth_worker, service, worker_profile):
        # Client places order
        order_response = auth_client.post('/api/v1/orders/', {
            'title': 'Fix my sink',
            'description': 'Need a plumber',
            'address': 'Tashkent, Chilonzor',
            'service': service.id,
            'worker': worker_profile.id,
        })
        assert order_response.status_code == 201
        order_id = order_response.data['id']

        # Worker accepts it
        response = auth_worker.patch(f'/api/v1/orders/{order_id}/accepted/')
        assert response.status_code == 200
        assert response.data['status'] == 'accepted'

    def test_cannot_cancel_completed_order(self, auth_client, auth_worker, service, worker_profile):
        # Place order
        order_response = auth_client.post('/api/v1/orders/', {
            'title': 'Fix my sink',
            'description': 'Need a plumber',
            'address': 'Tashkent, Chilonzor',
            'service': service.id,
            'worker': worker_profile.id,
        })
        assert order_response.status_code == 201
        order_id = order_response.data['id']

        # Worker accepts it first
        accept_response = auth_worker.patch(f'/api/v1/orders/{order_id}/accepted/')
        assert accept_response.status_code == 200  # ← make sure this passes

        # Then worker completes it
        complete_response = auth_worker.patch(f'/api/v1/orders/{order_id}/completed/')
        assert complete_response.status_code == 200  # ← make sure this passes

        # Client tries to cancel — should fail
        response = auth_client.patch(f'/api/v1/orders/{order_id}/cancelled/')
        assert response.status_code == 400