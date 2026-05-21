from rest_framework.exceptions import ValidationError
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet, ReadOnlyModelViewSet

from apps.models import (
    Category, Service, Conversation, Message, Order, OrderImage,
    ReviewImage, Favourite, WorkerProfile, Portfolio
)
from apps.permissions import IsClient, IsOwner, IsWorker
from apps.serializers import (
    CategorySerializer, ServiceSerializer, ConversationSerializer, MessageSerializer,
    OrderSerializer, OrderImageSerializer, ReviewImageSerializer,
    FavouriteSerializer, UserSerializer, WorkerProfileSerializer, PortfolioSerializer
)


class UserViewSet(GenericViewSet, mixins.RetrieveModelMixin, mixins.UpdateModelMixin):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class WorkerProfileViewSet(ModelViewSet):
    serializer_class = WorkerProfileSerializer

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'create']:
            return [IsAuthenticated(), IsOwner()]

        return [AllowAny(), ]

    def get_queryset(self):
        return WorkerProfile.objects.select_related('user').all()

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)


class PortfolioViewSet(ModelViewSet):
    serializer_class = PortfolioSerializer

    def get_queryset(self):
        return Portfolio.objects.filter(worker__user=self.request.user)

    def perform_create(self, serializer):
        worker_profile = self.request.user.worker_profile
        serializer.save(worker=worker_profile)


class CategoryViewSet(ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


class ServiceViewSet(ModelViewSet):
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
        return serializer.save(worker=self.request.user.worker_profile)


class ConversationViewSet(ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Conversation.objects.filter(
            client=user
        ) | Conversation.objects.filter(
            worker=user
        )


class MessageViewSet(ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(
            conversation__client=user
        ) | Message.objects.filter(
            conversation__worker=user
        )

    def perform_create(self, serializer):
        return serializer.save(sender=self.request.user)


class OrderViewSet(ModelViewSet):
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == 'worker':
            return Order.objects.filter(worker__user=user)

        return Order.objects.filter(client=user)

    def perform_create(self, serializer):
        return serializer.save(client=self.request.user)

    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated, IsWorker])
    def accepted(self, request, pk=None):
        order = self.get_object()
        order.status = 'accepted'
        order.save()
        return Response({'status': 'accepted'})

    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated, IsWorker])
    def completed(self, request, pk=None):
        order = self.get_object()
        order.status = 'completed'
        order.save()
        return Response({'status': 'completed'})

    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated, IsClient])
    def cancelled(self, request, pk=None):
        order = self.get_object()
        if order.status == 'completed':
            raise ValidationError('order already completed!')

        order.status = 'cancelled'
        order.save()
        return Response({'status': 'cancelled'})


class OrderImageViewSet(ModelViewSet):
    serializer_class = OrderImageSerializer

    def get_queryset(self):
        return OrderImage.objects.filter(order__client=self.request.user)


class ReviewViewSet(GenericViewSet, mixins.CreateModelMixin, mixins.ListModelMixin):
    serializer_class = ReviewImageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ReviewImage.objects.filter(client=self.request.user)

    def perform_create(self, serializer):
        return serializer.save(client=self.request.user)


class ReviewImageViewSet(ModelViewSet):
    serializer_class = ReviewImageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ReviewImage.objects.filter(review__client=self.request.user)


class FavouriteViewSet(viewsets.GenericViewSet,
                       mixins.CreateModelMixin,
                       mixins.DestroyModelMixin,
                       mixins.ListModelMixin):
    serializer_class = FavouriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Favourite.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
