from rest_framework import serializers

from apps.catalog.models import Category, Favorite, Product


class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ("id", "name", "slug", "product_count")

    def get_product_count(self, obj):
        return getattr(obj, "product_count", 0)


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    is_favorite = serializers.SerializerMethodField()
    badge_label = serializers.CharField(source="get_badge_display", read_only=True)
    discount_percent = serializers.IntegerField(read_only=True)
    has_discount = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "slug",
            "category",
            "description",
            "price",
            "original_price",
            "weight",
            "image_url",
            "badge",
            "badge_label",
            "allergens",
            "is_month_pick",
            "discount_percent",
            "has_discount",
            "is_active",
            "is_favorite",
        )

    def get_is_favorite(self, obj):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False
        return obj.favorited_by.filter(user=user).exists()

    def get_has_discount(self, obj):
        return bool(obj.original_price and obj.original_price > obj.price)


class FavoriteSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.filter(is_active=True),
        source="product",
        write_only=True,
    )

    class Meta:
        model = Favorite
        fields = ("id", "product", "product_id", "created_at")
        read_only_fields = ("id", "created_at", "product")

    def create(self, validated_data):
        favorite, _ = Favorite.objects.get_or_create(
            user=self.context["request"].user,
            product=validated_data["product"],
        )
        return favorite
