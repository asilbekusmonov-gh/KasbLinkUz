from django.db.models import Q
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import CreateAPIView
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet, ReadOnlyModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from drf_spectacular.utils import extend_schema

from apps.filters import WorkerFilter
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
from apps.tasks import send_order_placed_email, send_order_status_email, send_welcome_email


@extend_schema(
    tags=["Users"]
)
class UserViewSet(GenericViewSet, mixins.RetrieveModelMixin, mixins.UpdateModelMixin):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self):
        return self.request.user

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class RegisterView(CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        send_welcome_email.delay(user.id)

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


@extend_schema(
    tags=['WorkerProfile']
)
class WorkerProfileViewSet(ModelViewSet):
    queryset = WorkerProfile.objects.all()
    serializer_class = WorkerProfileSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    filter_backends = [OrderingFilter, SearchFilter]
    filterset_class = WorkerFilter
    search_fields = 'user__username', 'worker_services__category'
    ordering_fields = 'rating',

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'create', 'destroy']:
            return [IsAuthenticated(), IsOwner(), IsWorker]

        return [AllowAny(), ]

    def get_queryset(self):
        return WorkerProfile.objects.select_related('user').all()

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)


@extend_schema(
    tags=["Portfolio"]
)
class PortfolioViewSet(ModelViewSet):
    queryset = Portfolio.objects.all()
    serializer_class = PortfolioSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        return Portfolio.objects.filter(worker__user=self.request.user)

    def perform_create(self, serializer):
        worker_profile = self.request.user.worker_profile
        serializer.save(worker=worker_profile)


@extend_schema(
    tags=["Category"]
)
class CategoryViewSet(ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


@extend_schema(tags=["Service"])
class ServiceViewSet(ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated(), IsWorker()]

    def get_queryset(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return Service.objects.filter(worker__user=self.request.user)

        return Service.objects.select_related('worker', 'category').all()

    def perform_create(self, serializer):
        worker_profile = self.request.user.worker_profile
        return serializer.save(worker=worker_profile)


@extend_schema(tags=["Conversation"])
class ConversationViewSet(ModelViewSet):
    queryset = Conversation.objects.all()

    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Conversation.objects.filter(
            Q(client=user) | Q(worker=user)
        )


@extend_schema(tags=["Message"])
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


@extend_schema(tags=["Order"])
class OrderViewSet(ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'worker':
            return Order.objects.filter(service__worker__user=user)
        return Order.objects.filter(client=user)

    def perform_create(self, serializer):
        order = serializer.save(client=self.request.user)
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
            raise ValidationError('Order is already completed.')
        order.status = 'cancelled'
        order.save()
        send_order_status_email.delay(order.id, 'cancelled')
        return Response({'status': 'cancelled'})


@extend_schema(tags=["OrderImage"])
class OrderImageViewSet(ModelViewSet):
    queryset = OrderImage.objects.all()
    serializer_class = OrderImageSerializer

    def get_queryset(self):
        return OrderImage.objects.filter(order__client=self.request.user)


@extend_schema(tags=["Review"])
class ReviewViewSet(GenericViewSet, mixins.CreateModelMixin, mixins.ListModelMixin):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Review.objects.filter(client=self.request.user)

    def perform_create(self, serializer):
        return serializer.save(client=self.request.user)


@extend_schema(tags=["ReviewImage"])
class ReviewImageViewSet(ModelViewSet):
    queryset = ReviewImage.objects.all()
    serializer_class = ReviewImageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ReviewImage.objects.filter(review__client=self.request.user)


@extend_schema(tags=["Favourite"])
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
