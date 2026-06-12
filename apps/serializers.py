from rest_framework.exceptions import ValidationError
from rest_framework.fields import ImageField as DRFImageField, CharField, HiddenField, CurrentUserDefault
from rest_framework.serializers import ModelSerializer

from apps.models import (
    Category,
    Service,
    Conversation,
    Message,
    Order,
    OrderImage,
    Review,
    ReviewImage,
    Favourite,
    User,
    WorkerProfile,
    Portfolio,
)
from apps.models.users import City, District


class UserSerializer(ModelSerializer):
    password = CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "role",
            "phone_number",
            "profile_image",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
            "phone_number": {"required": False},
            "first_name": {"required": False},
            "last_name": {"required": False},
            "profile_image": {"required": False},
        }

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class WorkerProfileSerializer(ModelSerializer):
    user = HiddenField(default=CurrentUserDefault())
    profile_image = DRFImageField(required=False, use_url=True)

    class Meta:
        model = WorkerProfile
        fields = "__all__"
        read_only_fields = (
            "completed_orders_count",
            "rating",
        )

    def validate(self, data):
        request = self.context.get("request")

        if request and request.method == "POST":
            if WorkerProfile.objects.filter(user=request.user).exists():
                raise ValidationError("User can only have one worker profile")

        return data


class CityModelSerializer(ModelSerializer):
    class Meta:
        model = City
        fields = "__all__"


class DistrictModelSerializer(ModelSerializer):
    class Meta:
        model = District
        fields = "__all__"


class PortfolioSerializer(ModelSerializer):
    class Meta:
        model = Portfolio
        fields = "__all__"


class CategoryModelSerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class ServiceSerializer(ModelSerializer):
    worker = HiddenField(default=CurrentUserDefault())

    class Meta:
        model = Service
        fields = "__all__"

    def validate(self, data):
        min_price = data.get("min_price")
        max_price = data.get("max_price")

        if min_price > max_price or min_price <= 0:
            raise ValidationError("The error occurred in price!")
        return data


class ConversationSerializer(ModelSerializer):
    class Meta:
        model = Conversation
        fields = "__all__"


class MessageSerializer(ModelSerializer):
    sender = HiddenField(default=CurrentUserDefault())

    class Meta:
        model = Message
        fields = "__all__"

    def validate(self, data):
        request = self.context.get("request")
        conversation = data.get("conversation")
        if conversation and request:
            is_participant = conversation.client == request.user or conversation.worker == request.user

            if not is_participant:
                raise ValidationError("You are not participant of this conversation")

        return data


class OrderImageSerializer(ModelSerializer):
    class Meta:
        model = OrderImage
        fields = "__all__"


class OrderSerializer(ModelSerializer):
    client = HiddenField(default=CurrentUserDefault())
    order_images = OrderImageSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = "__all__"

    def validate(self, data):
        service = data.get("service")
        request = self.context.get("request")

        if request and service:
            if not service.active:
                raise ValidationError("You can not  place order on inactive service")

            if Order.objects.filter(client=request.user, service=service).exists():
                raise ValidationError("Client can not order  Their own service")

        return data


class ReviewImageSerializer(ModelSerializer):
    class Meta:
        model = ReviewImage
        fields = "__all__"


class ReviewSerializer(ModelSerializer):
    client = HiddenField(default=CurrentUserDefault())
    review_images = ReviewImageSerializer(many=True, read_only=True)

    class Meta:
        model = Review
        fields = "__all__"

    def validate(self, data):
        order = data.get("order")
        request = self.context.get("request")

        if order and request:
            if order.status != "completed":
                raise ValidationError("Order is not completed yet")

        if Review.objects.filter(client=request.user, order=order).exists():
            raise ValidationError("You can not review twice")

        if order.client != request.user:
            raise ValidationError("You can review your own review")

        return data


class FavouriteSerializer(ModelSerializer):
    client = HiddenField(default=CurrentUserDefault())

    class Meta:
        model = Favourite
        fields = "__all__"
