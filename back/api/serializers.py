# api/serializers.py
# Limits for text sent by anonymous visitors (spam protection, no DB migration).
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers

from .categories import category_ancestors
from .models import (
    AboutContent,
    Banner,
    Brand,
    Category,
    ContactInfo,
    ContactMessage,
    Feature,
    FeatureValue,
    Image,
    InfoPage,
    NewsItem,
    Order,
    OrderItem,
    Product,
    ProductDocument,
    ProductFeature,
    ProductQuestion,
    ProductReview,
)
from .pricing import discount_percent
from .validators import validate_safe_link

REVIEW_TEXT_MAX_LENGTH = 2000
QUESTION_TEXT_MAX_LENGTH = 1000
CONTACT_MESSAGE_MAX_LENGTH = 3000
ORDER_COMMENT_MAX_LENGTH = 1000


class BannerSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Banner
        fields = ["id", "title", "description", "image", "link", "order", "is_active"]

    def get_image(self, obj):
        if obj.image:
            try:
                return obj.image.url
            except Exception:
                return str(obj.image)
        return None

    def validate_link(self, value):
        # Rendered as <a :href> on the site: block javascript:/data: URLs.
        return validate_safe_link(value)


class ImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Image
        fields = ["id", "image", "is_main", "order"]

    def get_image(self, obj):
        if obj.image:
            try:
                return obj.image.url
            except Exception:
                return str(obj.image)
        return None


class ProductFeatureSerializer(serializers.ModelSerializer):
    feature_name = serializers.CharField(source="feature.name", read_only=True, required=False)
    # Heading of the characteristic (Feature.group); the compare page groups rows by it.
    group_name = serializers.CharField(source="feature.group", read_only=True, default="")
    feature_id = serializers.PrimaryKeyRelatedField(
        source="feature", queryset=Feature.objects.all(), required=False, allow_null=True
    )
    value_id = serializers.PrimaryKeyRelatedField(
        source="value", queryset=FeatureValue.objects.all(), required=False, allow_null=True
    )
    value_name = serializers.SerializerMethodField()

    class Meta:
        model = ProductFeature
        fields = ["id", "feature_name", "group_name", "feature_id", "value_id", "value_name"]

    def get_value_name(self, obj):
        """Safely get the value text from the FeatureValue object"""
        if obj.value:
            return obj.value.value
        return None


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    products_count = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "image", "parent", "children", "products_count"]

    def get_image(self, obj):
        if obj.image:
            try:
                return obj.image.url
            except Exception:
                return str(obj.image)
        return None

    def get_children(self, obj):
        # Categories already above this one are skipped, so a broken tree with a
        # cycle cannot recurse forever.
        ancestors = self.context.get("_category_ancestors", frozenset()) | {obj.id}
        children = obj.children.exclude(id__in=ancestors).order_by("order", "name")
        context = {**self.context, "_category_ancestors": ancestors}
        return CategorySerializer(children, many=True, context=context).data

    def get_products_count(self, obj):
        # Use annotated value from viewset when available (avoids N+1 query)
        if hasattr(obj, "direct_products_count"):
            return obj.direct_products_count
        return obj.products.count()


class BrandSerializer(serializers.ModelSerializer):
    # expose `image` property (frontend expects `image`) while the model field is `logo`
    image = serializers.SerializerMethodField()

    class Meta:
        model = Brand
        fields = ["id", "name", "slug", "image", "description"]

    def get_image(self, obj):
        if obj.logo:
            try:
                return obj.logo.url
            except Exception:
                return str(obj.logo)
        return None


COMMERCE_FIELDS = ["old_price", "discount_percent", "stock_quantity", "status", "status_label"]


class CommerceFieldsMixin(serializers.Serializer):
    """Old price with the computed discount, stock and the status label (like shop.nag.uz cards)."""

    discount_percent = serializers.SerializerMethodField()
    status_label = serializers.SerializerMethodField()

    def get_discount_percent(self, obj):
        return discount_percent(obj.price, obj.old_price)

    def get_status_label(self, obj):
        return Product.STATUS_LABELS.get(obj.status, "")


class ProductListSerializer(CommerceFieldsMixin, serializers.ModelSerializer):
    """Облегченный сериализатор для списка - минимум данных для быстрой загрузки"""

    images = serializers.SerializerMethodField()
    main_image = serializers.SerializerMethodField()
    category_name = serializers.CharField(source="category.name", read_only=True)
    brand = BrandSerializer(read_only=True)
    description = serializers.CharField(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "price",
            "is_available",
            "images",
            "main_image",
            "category_name",
            "brand",
            "manufacturer_sku",
            "internal_sku",
            "description",
            *COMMERCE_FIELDS,
        ]

    def get_images(self, obj):
        """Только первое изображение для списка"""
        images = list(obj.images.all())
        if not images:
            return []
        main = next((img for img in images if img.is_main), images[0])
        return [ImageSerializer(main, context=self.context).data]

    def get_main_image(self, obj):
        """Для обратной совместимости"""
        images = list(obj.images.all())
        if not images:
            return None
        main = next((img for img in images if img.is_main), images[0])
        return ImageSerializer(main, context=self.context).data


class ProductDocumentSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    ext = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()

    class Meta:
        model = ProductDocument
        fields = ["id", "title", "url", "ext", "size", "order"]

    def get_url(self, obj):
        return obj.file.url if obj.file else None

    def get_ext(self, obj):
        return obj.file.name.rsplit(".", 1)[-1].lower() if obj.file else ""

    def get_size(self, obj):
        try:
            return obj.file.size
        except (OSError, ValueError):  # file missing on disk
            return None


class ProductDetailSerializer(CommerceFieldsMixin, serializers.ModelSerializer):
    breadcrumbs = serializers.SerializerMethodField()
    feature_groups = serializers.SerializerMethodField()
    related = serializers.SerializerMethodField()
    documents = ProductDocumentSerializer(many=True, read_only=True)
    images = ImageSerializer(many=True, read_only=True)
    features = ProductFeatureSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "brand",
            "name",
            "slug",
            "description",
            "price",
            "is_available",
            "category",
            "images",
            "features",
            "manufacturer_sku",
            "internal_sku",
            "created_at",
            "updated_at",
            "breadcrumbs",
            "feature_groups",
            "related",
            "documents",
            *COMMERCE_FIELDS,
        ]

    MAX_RELATED = 20

    def get_breadcrumbs(self, obj):
        """Categories from the root down to the product's own category."""
        own = {"name": obj.category.name, "slug": obj.category.slug}
        return [*category_ancestors(obj.category), own]

    def get_feature_groups(self, obj):
        """Characteristics table: groups by Feature.group ("Общие" when empty, shown first),
        rows by Feature.order then name; several values of one characteristic in one row."""
        rows: dict = {}
        links = obj.features.select_related("feature", "value").exclude(feature=None)
        for pf in links.exclude(value=None).order_by("id"):
            f = pf.feature
            key = (f.group.strip() or "Общие", f.order, f.name)
            values = rows.setdefault(key, [])
            text = pf.value.value.strip()
            # "30" of a characteristic measured in "м" reads "30 м"; "до 40 м" stays as typed.
            if f.unit and not text.endswith(f.unit):
                text = f"{text} {f.unit}"
            if text not in values:
                values.append(text)
        groups: dict = {}
        for (group, _order, name), values in sorted(rows.items(), key=lambda kv: kv[0][1:]):
            groups.setdefault(group, []).append({"name": name, "values": values})
        ordered = sorted(groups.items(), key=lambda kv: kv[0] != "Общие")
        return [{"group": g, "items": items} for g, items in ordered]

    def get_related(self, obj):
        products = (
            obj.related.select_related("category", "brand")
            .prefetch_related("images")
            .order_by("-is_available", "name")[: self.MAX_RELATED]
        )
        return ProductListSerializer(products, many=True, context=self.context).data


class NewsItemSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    preview = serializers.SerializerMethodField()

    class Meta:
        model = NewsItem
        fields = ["id", "title", "slug", "preview", "image", "pub_date"]

    def get_image(self, obj):
        if obj.image:
            try:
                return obj.image.url
            except Exception:
                return str(obj.image)
        return None

    def get_preview(self, obj):
        if obj.preview:
            try:
                return obj.preview.url
            except Exception:
                return str(obj.preview)
        return None


class NewsDetailSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    preview = serializers.SerializerMethodField()

    class Meta:
        model = NewsItem
        fields = ["id", "title", "slug", "content", "preview", "image", "pub_date"]

    def get_image(self, obj):
        if obj.image:
            try:
                return obj.image.url
            except Exception:
                return str(obj.image)
        return None

    def get_preview(self, obj):
        if obj.preview:
            try:
                return obj.preview.url
            except Exception:
                return str(obj.preview)
        return None


class AboutContentSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = AboutContent
        fields = ["title", "content", "image"]

    def get_image(self, obj):
        if obj.image:
            try:
                return obj.image.url
            except Exception:
                return str(obj.image)
        return None


class ContactInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactInfo
        fields = [
            "phone",
            "email",
            "address",
            "map_url",
            "instagram",
            "telegram",
            "whatsapp",
            "facebook",
            "working_hours",
        ]


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "message"]
        extra_kwargs = {"message": {"max_length": CONTACT_MESSAGE_MAX_LENGTH}}


class ProductReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReview
        fields = [
            "id",
            "product",
            "author_name",
            "rating",
            "text",
            "created_at",
            "is_published",
            "admin_reply",
            "admin_reply_date",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "is_published",
            "admin_reply",
            "admin_reply_date",
            "product",
        ]
        extra_kwargs = {"text": {"max_length": REVIEW_TEXT_MAX_LENGTH}}


class ProductQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductQuestion
        fields = [
            "id",
            "product",
            "author_name",
            "text",
            "created_at",
            "is_published",
            "admin_reply",
            "admin_reply_date",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "is_published",
            "admin_reply",
            "admin_reply_date",
            "product",
        ]
        extra_kwargs = {"text": {"max_length": QUESTION_TEXT_MAX_LENGTH}}


# ============ ADMIN SERIALIZERS ============


class CategoryAdminSerializer(serializers.ModelSerializer):
    products_count = serializers.SerializerMethodField()
    parent_name = serializers.CharField(source="parent.name", read_only=True)
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        if obj.image:
            try:
                return obj.image.url
            except Exception:
                return str(obj.image)
        return None

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "parent", "parent_name", "image", "order", "products_count"]

    def validate_parent(self, value):
        # A category under itself or under its own subcategory would make a cycle:
        # the whole branch would disappear from the site.
        if value is not None and self.instance is not None:
            from .categories import is_self_or_descendant

            if is_self_or_descendant(value.id, self.instance.id):
                raise serializers.ValidationError(
                    "Нельзя выбрать родителем сам каталог или его подкаталог."
                )
        return value

    def get_products_count(self, obj):
        return obj.products.count()


class ProductAdminSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    brand_name = serializers.CharField(source="brand.name", read_only=True)
    images_count = serializers.SerializerMethodField()
    main_image = serializers.SerializerMethodField()
    # Inline данные для редактирования
    images = serializers.SerializerMethodField()
    features = serializers.SerializerMethodField()
    related = serializers.SerializerMethodField()
    documents = ProductDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "price",
            "related",
            "documents",
            "category",
            "category_name",
            "brand",
            "brand_name",
            "is_available",
            "old_price",
            "stock_quantity",
            "status",
            "is_recommended",
            "manufacturer_sku",
            "internal_sku",
            "created_at",
            "images_count",
            "main_image",
            "images",
            "features",
        ]

    def get_related(self, obj):
        """Chosen related products with what the admin form shows for each."""
        return [
            {"id": p.id, "name": p.name, "internal_sku": p.internal_sku}
            for p in obj.related.order_by("name")
        ]

    def get_images_count(self, obj):
        return obj.images.count()

    def get_main_image(self, obj):
        main = obj.images.filter(is_main=True).first()
        if not main:
            main = obj.images.first()
        if main and main.image:
            try:
                return main.image.url
            except Exception:
                return str(main.image)
        return None

    def get_images(self, obj):
        return [
            {
                "id": img.id,
                "image": img.image.url if img.image else None,
                "is_main": img.is_main,
                "order": img.order,
            }
            for img in obj.images.all().order_by("order")
        ]

    def get_features(self, obj):
        return [
            {
                "id": pf.id,
                "feature_id": pf.feature_id,
                "feature_name": pf.feature.name if pf.feature else None,
                "value_id": pf.value_id,
                "value_text": pf.value.value if pf.value else None,
            }
            for pf in obj.features.all().select_related("feature", "value")
        ]


class BrandAdminSerializer(serializers.ModelSerializer):
    products_count = serializers.SerializerMethodField()
    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = Brand
        fields = [
            "id",
            "name",
            "slug",
            "logo",
            "logo_url",
            "description",
            "created_at",
            "products_count",
        ]

    def get_products_count(self, obj):
        return obj.products.count()

    def get_logo_url(self, obj):
        if obj.logo:
            return obj.logo.url
        return None

    def validate_logo(self, value):
        if value:
            from .uploads import validate_uploaded_image

            ok, error = validate_uploaded_image(value)
            if not ok:
                raise serializers.ValidationError(error)
        return value


class FeatureAdminSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    values_count = serializers.SerializerMethodField()
    values = serializers.SerializerMethodField()
    value_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False, allow_empty=True
    )

    class Meta:
        model = Feature
        fields = [
            "id",
            "name",
            "category",
            "category_name",
            "group",
            "order",
            "filter_type",
            "unit",
            "values_count",
            "values",
            "value_ids",
        ]

    def validate(self, data):
        """Проверка уникальности названия характеристики в рамках категории"""
        name = data.get("name")
        category = data.get("category")

        # При обновлении исключаем текущий объект из проверки
        instance = self.instance
        queryset = Feature.objects.filter(name=name, category=category)

        if instance:
            queryset = queryset.exclude(pk=instance.pk)

        if queryset.exists():
            raise serializers.ValidationError(
                {"name": f'Характеристика "{name}" уже существует в категории "{category.name}"'}
            )

        return data

    def create(self, validated_data):
        value_ids = validated_data.pop("value_ids", [])
        feature = Feature.objects.create(**validated_data)
        if value_ids:
            feature.values.set(value_ids)
        return feature

    def update(self, instance, validated_data):
        value_ids = validated_data.pop("value_ids", None)
        instance = super().update(instance, validated_data)
        if value_ids is not None:
            instance.values.set(value_ids)
        return instance

    def get_values_count(self, obj):
        return obj.values.count()

    def get_values(self, obj):
        """Возвращает привязанные значения характеристики"""
        return [{"id": v.id, "value": v.value} for v in obj.values.all()[:20]]


class FeatureValueAdminSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    features_info = serializers.SerializerMethodField()

    class Meta:
        model = FeatureValue
        fields = ["id", "value", "category", "category_name", "features_info"]

    def get_features_info(self, obj):
        """Возвращает список привязанных характеристик"""
        return [{"id": f.id, "name": f.name} for f in obj.features.all()]


class NewsAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsItem
        fields = ["id", "title", "slug", "preview", "content", "image", "pub_date", "is_published"]
        read_only_fields = ["pub_date"]


class AboutContentAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutContent
        fields = ["id", "title", "content", "image", "updated_at"]
        read_only_fields = ["updated_at"]


class ContactInfoAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactInfo
        fields = [
            "id",
            "phone",
            "email",
            "address",
            "map_url",
            "instagram",
            "telegram",
            "whatsapp",
            "facebook",
            "working_hours",
            "updated_at",
        ]
        read_only_fields = ["updated_at"]


class ProductReviewAdminSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = ProductReview
        fields = [
            "id",
            "product",
            "product_name",
            "author_name",
            "rating",
            "text",
            "created_at",
            "is_published",
            "admin_reply",
            "admin_reply_date",
        ]
        read_only_fields = ["id", "created_at"]


class ProductQuestionAdminSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = ProductQuestion
        fields = [
            "id",
            "product",
            "product_name",
            "author_name",
            "text",
            "created_at",
            "is_published",
            "admin_reply",
            "admin_reply_date",
        ]
        read_only_fields = ["id", "created_at"]


class ContactMessageAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ["id", "name", "email", "message", "created_at", "is_processed"]
        read_only_fields = ["name", "email", "message", "created_at"]


class ImageAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ["id", "product", "image", "is_main", "order"]

    def validate_image(self, value):
        from .uploads import validate_uploaded_image

        ok, error = validate_uploaded_image(value)
        if not ok:
            raise serializers.ValidationError(error)
        return value


# ============ AUTH SERIALIZERS ============


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_staff",
            "is_superuser",
            "date_joined",
            "last_login",
        ]
        read_only_fields = ["id", "date_joined", "last_login"]


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value


class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "first_name", "last_name"]


MAX_ORDER_ITEMS = 50
MAX_ITEM_QUANTITY = 999


class OrderItemSerializer(serializers.ModelSerializer):
    """Client sends product id + quantity. Name, SKU and price are always taken
    from the catalog on the server; values sent by the client are ignored."""

    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.IntegerField(min_value=1, max_value=MAX_ITEM_QUANTITY)

    class Meta:
        model = OrderItem
        fields = ["product", "product_name", "product_sku", "price", "quantity"]
        read_only_fields = ["product_name", "product_sku", "price"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "customer_name",
            "customer_phone",
            "customer_email",
            "customer_telegram",
            "comment",
            "status",
            "created_at",
            "items",
        ]
        read_only_fields = ["id", "status", "created_at"]
        extra_kwargs = {"comment": {"max_length": ORDER_COMMENT_MAX_LENGTH}}

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("Заказ должен содержать хотя бы один товар.")
        if len(value) > MAX_ORDER_ITEMS:
            raise serializers.ValidationError(f"Не более {MAX_ORDER_ITEMS} позиций в заказе.")
        return value

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        with transaction.atomic():
            order = Order.objects.create(**validated_data)
            for item_data in items_data:
                product = item_data["product"]
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    product_sku=product.manufacturer_sku or "",
                    price=product.price,
                    quantity=item_data["quantity"],
                )
        return order

    def update(self, instance, validated_data):
        # Order lines are fixed once the customer has sent the order.
        if "items" in validated_data:
            raise serializers.ValidationError({"items": "Состав заказа нельзя изменить."})
        return super().update(instance, validated_data)


class OrderAdminSerializer(OrderSerializer):
    """Сериализатор для администратора - включает статус"""

    class Meta(OrderSerializer.Meta):
        read_only_fields = ["id", "created_at"]


class InfoPageListSerializer(serializers.ModelSerializer):
    class Meta:
        model = InfoPage
        fields = ["slug", "title"]


class InfoPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = InfoPage
        fields = ["slug", "title", "content", "updated_at"]


class InfoPageAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = InfoPage
        fields = ["id", "title", "slug", "content", "order", "is_published", "updated_at"]
        read_only_fields = ["updated_at"]
        extra_kwargs = {"slug": {"required": False}}
