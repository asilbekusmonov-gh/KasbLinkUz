from django.db.models import Q
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet, ReadOnlyModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status

from apps.models import (
    Category, Service, Conversation, Message, Order, OrderImage,
    ReviewImage, Favourite, WorkerProfile, Portfolio, Review, User
)
from apps.permissions import IsClient, IsOwner, IsWorker
from apps.serializers import (
    CategorySerializer, ServiceSerializer, ConversationSerializer, MessageSerializer,
    OrderSerializer, OrderImageSerializer, ReviewImageSerializer,
    FavouriteSerializer, UserSerializer, WorkerProfileSerializer, PortfolioSerializer, ReviewSerializer
)
from apps.tasks import send_mail_task, send_order_placed_email, send_order_status_email


class UserViewSet(GenericViewSet, mixins.RetrieveModelMixin, mixins.UpdateModelMixin):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class WorkerProfileViewSet(ModelViewSet):
    queryset = WorkerProfile.objects.all()
    serializer_class = WorkerProfileSerializer

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'create', 'destroy']:
            return [IsAuthenticated(), IsOwner()]

        return [AllowAny(), ]

    def get_queryset(self):
        return WorkerProfile.objects.select_related('user').all()

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)


class PortfolioViewSet(ModelViewSet):
    queryset = Portfolio.objects.all()
    serializer_class = PortfolioSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Portfolio.objects.none()

        if not self.request.user.is_authenticated:
            return Portfolio.objects.none()

        return Portfolio.objects.filter(worker__user=self.request.user)

    def perform_create(self, serializer):
        worker_profile = self.request.user.worker_profile
        serializer.save(worker=worker_profile)


class CategoryViewSet(ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


class ServiceViewSet(ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated(), IsWorker()]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Service.objects.none()
        if self.request.user.is_authenticated:
            if self.action in ['create', 'update', 'partial_update', 'destroy']:
                return Service.objects.filter(worker__user=self.request.user)

        return Service.objects.select_related('worker', 'category').all()

    def perform_create(self, serializer):
        worker_profile = self.request.user.worker_profile
        return serializer.save(worker=worker_profile)


class ConversationViewSet(ModelViewSet):
    queryset = Conversation.objects.all()

    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Conversation.objects.filter(
            Q(client=user) | Q(worker=user)
        )


class MessageViewSet(ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(
            Q(conversation__client=user) |
            Q(conversation__worker=user)
        )

    def perform_create(self, serializer):
        return serializer.save(sender=self.request.user)


class OrderViewSet(ModelViewSet):
    serializer_class = OrderSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()

        user = self.request.user

        if not user.is_authenticated:
            return Order.objects.none()

        if user.role == 'worker':
            return Order.objects.filter(worker__user=user)

        return Order.objects.filter(client=user)

    def perform_create(self, serializer):
        order = serializer.save(client=self.request.user)  # save and store it
        send_order_placed_email.delay(order.id)


@action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated, IsWorker])
def accepted(self, request, pk=None):
    order = self.get_object()
    order.status = 'accepted'
    order.save()

    send_order_status_email.delay(order.id, 'accepted')

    return Response({'status': 'accepted'})


@action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated, IsWorker])
def completed(self, request, pk=None):
    order = self.get_object()
    order.status = 'completed'
    order.save()

    send_order_status_email.delay(order.id, 'completed')

    return Response({'status': 'completed'})


@action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated, IsClient])
def cancelled(self, request, pk=None):
    order = self.get_object()
    if order.status == 'completed':
        raise ValidationError('order already completed!')

    order.status = 'cancelled'
    order.save()

    send_order_status_email.delay(order.id, 'cancelled')

    return Response({'status': 'cancelled'})


class OrderImageViewSet(ModelViewSet):
    queryset = OrderImage.objects.all()
    serializer_class = OrderImageSerializer

    def get_queryset(self):
        return OrderImage.objects.filter(order__client=self.request.user)


class ReviewViewSet(GenericViewSet, mixins.CreateModelMixin, mixins.ListModelMixin):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Review.objects.filter(client=self.request.user)

    def perform_create(self, serializer):
        return serializer.save(client=self.request.user)


class ReviewImageViewSet(ModelViewSet):
    queryset = ReviewImage.objects.all()
    serializer_class = ReviewImageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ReviewImage.objects.filter(review__client=self.request.user)


class FavouriteViewSet(viewsets.GenericViewSet,
                       mixins.CreateModelMixin,
                       mixins.DestroyModelMixin,
                       mixins.ListModelMixin):
    queryset = Favourite.objects.all()
    serializer_class = FavouriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Favourite.objects.filter(client=self.request.user)

    def perform_create(self, serializer):
        serializer.save(client=self.request.user)


class RegisterView(CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        send_mail_task.delay(user.id)

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user": {
                    "id": user.id,
                    "username": user.username,
                },
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_201_CREATED
        )
