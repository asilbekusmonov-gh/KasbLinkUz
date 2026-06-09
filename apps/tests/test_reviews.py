import pytest
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
import datetime

from apps.models import User, WorkerProfile, Category, Service, Order
from django.utils import timezone


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
        email='worker@gmail.comm',
        password='123456',
        role='worker',
        phone_number='901111112'
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
    return Category.objects.create(
        name='Test category',
    )


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
def order(client_user, worker_profile, service):
    return Order.objects.create(
        title='Test order',
        description='Test description',
        address='Test address',
        client=client_user,
        service=service,
        worker=worker_profile,

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


@pytest.fixture
def completed_order(order, auth_worker):
    # Accept first
    accept_response = auth_worker.patch(reverse('order-accepted', args=[order.id]))
    assert accept_response.status_code == 200, f"Accept failed: {accept_response.data}"

    # Then complete
    complete_response = auth_worker.patch(reverse('order-completed', args=[order.id]))
    assert complete_response.status_code == 200, f"Complete failed: {complete_response.data}"

    # Refresh from database
    order.refresh_from_db()
    assert order.status == 'completed', f"Order status is {order.status}"
    return order


@pytest.mark.django_db
class TestReview:
    def test_client_can_review_completed_order(self, completed_order, auth_client):
        url = reverse('review-list')
        response = auth_client.post(url, {
            'order': completed_order.id,
            'rating': 5,
            'comment': 'Great service!'
        })
        print("RESPONSE DATA:", response.data)  # ← make sure this line exists
        assert response.status_code == status.HTTP_201_CREATED

    def test_cannot_review_pending_order(self, auth_client, order):
        url = reverse('review-list')
        response = auth_client.post(url, {
            'order': order.id,
            'rating': 5,
            'comment': 'Great service!'
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST
