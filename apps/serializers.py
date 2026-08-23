from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField, CurrentUserDefault, HiddenField, ListField, SerializerMethodField
from rest_framework.fields import ImageField as DRFImageField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer

from apps.models import (
    Category,
    Conversation,
    Favourite,
    Message,
    Notification,
    Order,
    OrderImage,
    Portfolio,
    Review,
    ReviewImage,
    Service,
    User,
    WorkerProfile,
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

    def validate_phone_number(self, value):
        if not value.isdigit():
            raise ValidationError("The error occurred in phone number!")

        return value


class WorkerProfileSerializer(ModelSerializer):
    user = HiddenField(default=CurrentUserDefault())
    user_id = CharField(source="user.id", read_only=True)
    user_detail = UserSerializer(source="user", read_only=True)
    profile_image = DRFImageField(required=False, use_url=True)
    bio = CharField(allow_blank=True, required=False)

    class Meta:
        model = WorkerProfile
        fields = "__all__"
        read_only_fields = (
            "completed_orders_count",
            "rating",
        )

    def validate(self, data):
        request = self.context.get("request")

        if request and request.method == "POST" and WorkerProfile.objects.filter(user=request.user).exists():
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


class CategoryModelSerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class WorkerProfileDetailSerializer(ModelSerializer):
    user_detail = UserSerializer(source="user", read_only=True)

    class Meta:
        model = WorkerProfile
        fields = [
            "id",
            "profile_image",
            "bio",
            "work_start_time",
            "work_end_time",
            "rating",
            "completed_orders_count",
            "is_available",
            "user_detail",
        ]


class PortfolioSerializer(ModelSerializer):
    worker_detail = WorkerProfileDetailSerializer(source="worker", read_only=True)
    category_detail = CategoryModelSerializer(source="category", read_only=True)
    description = CharField(allow_blank=True, required=False)

    class Meta:
        model = Portfolio
        fields = "__all__"
        read_only_fields = ("worker",)


class ServiceSerializer(ModelSerializer):
    worker = PrimaryKeyRelatedField(read_only=True)  # set by perform_create, returned in responses
    worker_detail = WorkerProfileDetailSerializer(source="worker", read_only=True)
    description = CharField(allow_blank=True, required=False)

    class Meta:
        model = Service
        fields = [
            "id",
            "name",
            "min_price",
            "max_price",
            "active",
            "description",
            "worker",
            "category",
            "worker_detail",
        ]

    def validate(self, data):
        min_price = data.get("min_price")
        max_price = data.get("max_price")

        if min_price is None or max_price is None:
            raise ValidationError("min_price va max_price kiritilishi shart!")

        if min_price <= 0:
            raise ValidationError("Minimal narx 0 dan katta bo'lishi kerak!")

        if min_price > max_price:
            raise ValidationError("Minimal narx maksimal narxdan katta bo'lmasligi kerak!")

        return data


class ConversationSerializer(ModelSerializer):
    client_detail = UserSerializer(source="client", read_only=True)
    worker_detail = UserSerializer(source="worker", read_only=True)

    class Meta:
        model = Conversation
        fields = [
            "id",
            "client",
            "worker",
            "client_detail",
            "worker_detail",
        ]


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
    reviews = PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "title",
            "description",
            "address",
            "status",
            "worker",
            "service",
            "client",
            "created_at",
            "updated_at",
            "order_images",
            "reviews",
        ]

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

    def validate(self, data):
        request = self.context.get("request")
        review = data.get("review")
        if request and review and review.client != request.user:
            raise ValidationError("You can only add images to your own review.")
        return data


class ReviewSerializer(ModelSerializer):
    client = HiddenField(default=CurrentUserDefault())
    client_detail = UserSerializer(source="client", read_only=True)
    review_images = ReviewImageSerializer(many=True, read_only=True)
    uploaded_images = ListField(
        child=DRFImageField(), write_only=True, required=False
    )
    comment = CharField(allow_blank=True, required=False)

    class Meta:
        model = Review
        fields = [
            "id",
            "order",
            "client",
            "client_detail",
            "rating",
            "comment",
            "review_images",
            "uploaded_images",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("created_at", "updated_at")

    def validate(self, data):
        order = data.get("order")
        request = self.context.get("request")

        if order and request and order.status != "completed":
            raise ValidationError("Order is not completed yet")

        if Review.objects.filter(client=request.user, order=order).exists():
            raise ValidationError("You can not review twice")

        if order.client != request.user:
            raise ValidationError("You can review your own review")

        return data

    def create(self, validated_data):
        uploaded_images = validated_data.pop("uploaded_images", [])

        request = self.context.get("request")
        if request and request.FILES:
            files = (
                request.FILES.getlist("uploaded_images")
                or request.FILES.getlist("images")
                or request.FILES.getlist("review_images")
            )
            for f in files:
                if f not in uploaded_images:
                    uploaded_images.append(f)

        review = Review.objects.create(**validated_data)

        for image in uploaded_images:
            ReviewImage.objects.create(review=review, image=image)

        return review


class FavouriteSerializer(ModelSerializer):
    client = HiddenField(default=CurrentUserDefault())

    class Meta:
        model = Favourite
        fields = "__all__"


class NotificationSerializer(ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"

