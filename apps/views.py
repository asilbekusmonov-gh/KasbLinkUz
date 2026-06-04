from django.db.models import Q, Count
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import CreateAPIView, ListAPIView
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
    permission_classes = [IsAuthenticated & IsOwner]
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
    queryset = WorkerProfile.objects.select_related('user').all()
    serializer_class = WorkerProfileSerializer
    permission_classes = [(IsAuthenticated & IsOwner & IsWorker) | AllowAny]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    filter_backends = [OrderingFilter, SearchFilter]
    filterset_class = WorkerFilter
    search_fields = [
        'user__username',
        'worker_services__category'
    ]
    ordering_fields = ['rating']

    def get_queryset(self):
        qs = super().get_queryset()

        if self.action in ['update', 'partial_update', 'destroy']:
            return qs.filter(worker__user=self.request.user)

        return qs.select_related('user').all()


@extend_schema(
    tags=["Portfolio"]
)
class PortfolioViewSet(ModelViewSet):
    queryset = Portfolio.objects.all()
    serializer_class = PortfolioSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(worker__user=self.request.user)

    def perform_create(self, serializer):
        if not hasattr(self.request.user, 'worker_profile'):
            raise ValidationError('Worker profile not found.')
        worker_profile = self.request.user.worker_profile
        serializer.save(worker=worker_profile)


@extend_schema(
    tags=["Category"]
)
class CategoryListApi(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


@extend_schema(tags=["Service"])
class ServiceViewSet(ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]  # anyone can browse
        return [IsAuthenticated(), IsWorker()]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action in ['update', 'partial_update', 'destroy']:
            return qs.filter(worker__user=self.request.user)

        return qs.select_related('worker', 'category').all()

    def perform_create(self, serializer):
        worker_profile = self.request.user.worker_profile
        return serializer.save(worker=worker_profile)


@extend_schema(tags=["Conversation"])
class ConversationViewSet(ModelViewSet):
    queryset = Conversation.objects.all()

    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        return qs.filter(
            Q(client=user) | Q(worker=user)
        )


@extend_schema(tags=["Message"])
class MessageViewSet(ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        return qs.filter(
            Q(conversation__client=user) |
            Q(conversation__worker=user)
        )

    def perform_create(self, serializer):
        return serializer.save(sender=self.request.user)


@extend_schema(tags=["Order"])
class OrderViewSet(ModelViewSet):
    queryset = Order.objects.select_related(
        'client',
        'service',
        'service__worker'
    )
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_worker:
            return qs.filter(service__worker__user=user)
        return qs.filter(client=user)

    def perform_create(self, serializer):
        order = serializer.save()
        send_order_placed_email.delay(order.id)

    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated, IsWorker])
    def accepted(self, request, pk=None):
        order = self.get_object()
        order.status = Order.Status.ACCEPTED
        order.save()
        send_order_status_email.delay(order.id, 'accepted')
        return Response({'status': 'accepted'})

    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated, IsWorker])
    def completed(self, request, pk=None):
        order = self.get_object()
        if order.status != Order.Status.ACCEPTED:
            raise ValidationError(
                'Only accepted orders can be completed.'
            )
        order.status = Order.Status.COMPLETED
        order.save()
        send_order_status_email.delay(order.id, 'completed')
        return Response({'status': 'completed'})

    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated, IsClient])
    def cancelled(self, request, pk=None):
        order = self.get_object()
        if order.status == Order.Status.COMPLETED:
            raise ValidationError('Order is already completed.')
        order.status = Order.Status.CANCELLED
        order.save()
        send_order_status_email.delay(order.id, 'cancelled')
        return Response({'status': 'cancelled'})


@extend_schema(tags=["OrderImage"])
class OrderImageViewSet(ModelViewSet):
    queryset = OrderImage.objects.all()
    serializer_class = OrderImageSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(order__client=self.request.user)


@extend_schema(tags=["Review"])
class ReviewViewSet(GenericViewSet, mixins.CreateModelMixin, mixins.ListModelMixin):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(client=self.request.user)


@extend_schema(tags=["ReviewImage"])
class ReviewImageViewSet(ModelViewSet):
    queryset = ReviewImage.objects.all()
    serializer_class = ReviewImageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(review__client=self.request.user)


@extend_schema(tags=["Favourite"])
class FavouriteViewSet(viewsets.GenericViewSet,
                       mixins.CreateModelMixin,
                       mixins.DestroyModelMixin,
                       mixins.ListModelMixin):
    queryset = Favourite.objects.all()
    serializer_class = FavouriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(client=self.request.user)
