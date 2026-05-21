from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from apps.models import (
    Category, Service, Conversation, Message, Order, OrderImage,
    Review, ReviewImage, Favourite, User, WorkerProfile, Portfolio
)
from apps.models.users import City, District


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'phone_number', 'profile_image']
        extra_kwargs = {'password': {'write_only': True}}


class WorkerProfileSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = WorkerProfile
        fields = '__all__'


class CityModelSerializer(ModelSerializer):
    class Meta:
        model = City
        fields = '__all__'


class DistrictModelSerializer(ModelSerializer):
    class Meta:
        model = District
        fields = '__all__'


class PortfolioSerializer(ModelSerializer):
    class Meta:
        model = Portfolio
        fields = '__all__'


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ServiceSerializer(ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'


class ConversationSerializer(ModelSerializer):
    class Meta:
        model = Conversation
        fields = '__all__'


class MessageSerializer(ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'


class OrderImageSerializer(ModelSerializer):
    class Meta:
        model = OrderImage
        fields = '__all__'


class OrderSerializer(ModelSerializer):
    order_images = OrderImageSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = '__all__'


class ReviewImageSerializer(ModelSerializer):
    class Meta:
        model = ReviewImage
        fields = '__all__'


class ReviewSerializer(ModelSerializer):
    review_images = ReviewImageSerializer(many=True, read_only=True)

    class Meta:
        model = Review
        fields = '__all__'


class FavouriteSerializer(ModelSerializer):
    class Meta:
        model = Favourite
        fields = '__all__'
