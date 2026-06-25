from django.contrib.auth import get_user_model
from django.db.models import Count
from django.utils.text import slugify
from rest_framework import serializers

from apps.catalog.models import Category, Product
from apps.catalog.serializers import CategorySerializer, ProductSerializer
from apps.feedback.models import ContactRequest
from apps.orders.models import Order
from apps.orders.serializers import OrderSerializer


User = get_user_model()


def build_unique_slug(name, *, instance=None):
    base_slug = slugify(name) or "product"
    slug = base_slug
    suffix = 1

    queryset = Product.objects.all()
    if instance is not None:
        queryset = queryset.exclude(pk=instance.pk)

    while queryset.filter(slug=slug).exists():
        suffix += 1
        slug = f"{base_slug}-{suffix}"

    return slug


class AdminUserSerializer(serializers.ModelSerializer):
    is_admin = serializers.SerializerMethodField()
    orders_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = ("id", "email", "name", "phone", "date_joined", "is_admin", "orders_count")

    def get_is_admin(self, obj):
        return bool(obj.is_staff or obj.is_superuser)


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    is_admin = serializers.BooleanField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ("email", "name", "phone", "is_admin")

    def validate_email(self, value):
        value = value.lower()
        queryset = User.objects.exclude(pk=self.instance.pk)
        if queryset.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует.")
        return value

    def validate(self, attrs):
        request = self.context["request"]
        is_admin = attrs.get("is_admin")
        if is_admin is False and self.instance.pk == request.user.pk:
            raise serializers.ValidationError(
                {"is_admin": "Нельзя снять права администратора у текущего аккаунта."}
            )
        return attrs

    def update(self, instance, validated_data):
        is_admin = validated_data.pop("is_admin", None)
        for field, value in validated_data.items():
            setattr(instance, field, value)

        if is_admin is not None:
            instance.is_staff = is_admin
            instance.is_superuser = is_admin

        instance.save()
        return instance


class AdminProductWriteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    category_slug = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field="slug",
        source="category",
    )
    original_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        allow_null=True,
    )
    badge_label = serializers.CharField(source="get_badge_display", read_only=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "slug",
            "description",
            "price",
            "original_price",
            "weight",
            "image_url",
            "badge",
            "badge_label",
            "allergens",
            "is_month_pick",
            "category_slug",
        )
        extra_kwargs = {
            "slug": {"required": False, "allow_blank": True},
            "weight": {"required": False, "allow_blank": True},
            "allergens": {"required": False, "allow_blank": True},
            "description": {"required": False, "allow_blank": True},
            "image_url": {"required": False, "allow_blank": True},
        }

    def validate(self, attrs):
        original_price = attrs.get("original_price")
        price = attrs.get("price", getattr(self.instance, "price", None))
        if original_price is not None and price is not None and original_price < price:
            raise serializers.ValidationError(
                {"original_price": "Старая цена должна быть больше или равна текущей цене."}
            )
        return attrs

    def create(self, validated_data):
        slug = validated_data.get("slug")
        validated_data["slug"] = build_unique_slug(slug or validated_data["name"])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        slug = validated_data.get("slug")
        if slug is not None:
            validated_data["slug"] = build_unique_slug(slug or validated_data["name"], instance=instance)
        elif "name" in validated_data and instance.slug == build_unique_slug(instance.name, instance=instance):
            validated_data["slug"] = build_unique_slug(validated_data["name"], instance=instance)
        return super().update(instance, validated_data)


class AdminOrderSerializer(OrderSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    user_name = serializers.CharField(source="user.name", read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta(OrderSerializer.Meta):
        fields = OrderSerializer.Meta.fields + ("user_id", "user_name", "user_email")


class AdminOrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ("status",)


class AdminFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactRequest
        fields = ("id", "name", "email", "phone", "message", "created_at", "processed")


def get_admin_dashboard_payload(request):
    users = User.objects.annotate(orders_count=Count("orders")).order_by("-date_joined")
    products = Product.objects.select_related("category").order_by("category__sort_order", "name")
    categories = Category.objects.annotate(product_count=Count("products")).all()
    orders = Order.objects.select_related("user").prefetch_related("items").all()
    feedback = ContactRequest.objects.all()

    return {
        "categories": CategorySerializer(categories, many=True).data,
        "products": ProductSerializer(products, many=True, context={"request": request}).data,
        "users": AdminUserSerializer(users, many=True).data,
        "orders": AdminOrderSerializer(orders, many=True).data,
        "feedback": AdminFeedbackSerializer(feedback, many=True).data,
    }
