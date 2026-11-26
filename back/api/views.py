# api/views.py
import csv
from decimal import Decimal

from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import DataError, IntegrityError
from django.db.models import Count, ProtectedError, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import filters, generics, status, viewsets
from rest_framework.decorators import action, api_view, authentication_classes, permission_classes
from rest_framework.exceptions import ValidationError

# DoS guards for public query parameters.
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .auth import revoke_all_refresh_tokens
from .catalog import build_facets, filter_products, parse_catalog_query, sort_products
from .categories import category_ancestors
from .csv_safety import safe_csv_cell
from .documents import validate_uploaded_document
from .filters import BrandFilter
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
    Product,
    ProductDocument,
    ProductFeature,
    ProductQuestion,
    ProductReview,
)
from .pagination import CatalogPagination, LargeListPagination, StandardResultsSetPagination
from .params import date_param, inline_list, int_param, price_value
from .serializers import (
    AboutContentAdminSerializer,
    AboutContentSerializer,
    BannerSerializer,
    BrandAdminSerializer,
    BrandSerializer,
    CategoryAdminSerializer,
    CategorySerializer,
    ChangePasswordSerializer,
    ContactInfoAdminSerializer,
    ContactInfoSerializer,
    ContactMessageAdminSerializer,
    ContactMessageSerializer,
    FeatureAdminSerializer,
    FeatureValueAdminSerializer,
    ImageAdminSerializer,
    InfoPageAdminSerializer,
    InfoPageListSerializer,
    InfoPageSerializer,
    NewsAdminSerializer,
    NewsDetailSerializer,
    NewsItemSerializer,
    OrderAdminSerializer,
    OrderSerializer,
    ProductAdminSerializer,
    ProductDetailSerializer,
    ProductDocumentSerializer,
    ProductListSerializer,
    ProductQuestionAdminSerializer,
    ProductQuestionSerializer,
    ProductReviewAdminSerializer,
    ProductReviewSerializer,
    UpdateProfileSerializer,
    UserSerializer,
)
from .slugs import make_slug, unique_slug
from .throttles import ORDER_THROTTLES, PUBLIC_WRITE_THROTTLES, LoginRateThrottle
from .uploads import validate_uploaded_image

MAX_FEATURE_FILTERS = 10  # each feature_<id> param adds a JOIN
MAX_BY_FEATURE_RESULTS = 100  # /products/by-feature/ returns a plain list
MAX_LIST_LIMIT = 100  # ?limit= on categories/news


def parse_limit(raw):
    """?limit= value: not a number or < 1 -> None (no slicing), else capped at MAX_LIST_LIMIT."""
    try:
        value = int(raw)
    except (TypeError, ValueError):
        return None
    if value < 1:
        return None
    return min(value, MAX_LIST_LIMIT)


# ============ JWT AUTH VIEWS ============
class AdminTokenObtainPairView(TokenObtainPairView):
    """
    JWT Login endpoint with rate limiting to prevent brute force attacks.
    """

    throttle_classes = [LoginRateThrottle]
    permission_classes = [AllowAny]
    # Staff-only issuance is enforced by SIMPLE_JWT['USER_AUTHENTICATION_RULE'].


class AdminTokenRefreshView(TokenRefreshView):
    """
    JWT Token refresh endpoint.
    """

    permission_classes = [AllowAny]


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_me(request):
    """
    Get current authenticated user information.
    """
    user = request.user
    if not user.is_staff:
        return Response(
            {"detail": "Only admin users can access this endpoint."},
            status=status.HTTP_403_FORBIDDEN,
        )

    return Response(
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
            "date_joined": user.date_joined.isoformat() if user.date_joined else None,
            "last_login": user.last_login.isoformat() if user.last_login else None,
        }
    )


@api_view(["POST"])
@authentication_classes([])  # a stale/expired Authorization header must not block logout
@permission_classes([AllowAny])
def admin_logout(request):
    """
    Logout: revokes the given refresh token. AllowAny so that logout still
    works when the access token has already expired; holding the refresh
    token is the proof needed to revoke it.
    """
    refresh = request.data.get("refresh") if isinstance(request.data, dict) else None
    if not refresh:
        return Response({"detail": "refresh token required"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        RefreshToken(refresh).blacklist()
    except TokenError:
        pass  # already invalid, expired or revoked: nothing left to revoke
    return Response({"detail": "Logout successful"}, status=status.HTTP_200_OK)


# ============ EXISTING VIEWS ============
@api_view(["GET"])
def features_tags_by_category(request):
    """Features of a category with their values, and all feature values of the category."""
    category_id = int_param(request.GET, "category")  # 400 on a non-number
    if category_id is None:
        return JsonResponse({"error": "category parameter is required"}, status=400)
    try:
        # Get all features with their values for this category
        features = Feature.objects.filter(category_id=category_id).prefetch_related("values")

        # Get all feature values for this category
        feature_values = FeatureValue.objects.filter(category_id=category_id)

        # Build features data with their values
        features_data = []
        for feature in features:
            feature_dict = {
                "id": feature.id,
                "name": feature.name,
                "values": [{"id": v.id, "value": v.value} for v in feature.values.all()],
            }
            features_data.append(feature_dict)

        # Build feature values data
        feature_values_data = list(feature_values.values("id", "value", "category_id"))

        return JsonResponse(
            {
                "features": features_data,
                "feature_values": feature_values_data,
            }
        )
    except Exception as e:
        import logging
        import traceback

        logging.error(f"Error in features_tags_by_category: {str(e)}\n{traceback.format_exc()}")
        return JsonResponse({"error": "Internal server error"}, status=500)


@api_view(["GET"])
def feature_values_by_feature(request):
    """Получить значения характеристики по её ID"""
    feature_id = int_param(request.GET, "feature_id")  # 400 on a non-number
    if feature_id is None:
        return JsonResponse({"error": "feature_id is required"}, status=400)

    try:
        # Get the feature and retrieve its values through ManyToMany relationship
        feature = Feature.objects.prefetch_related("values").get(id=feature_id)
        values = feature.values.all().values("id", "value")
        return JsonResponse({"values": list(values)})
    except Feature.DoesNotExist:
        return JsonResponse({"error": "Feature not found"}, status=404)
    except Exception:
        import logging

        logging.getLogger(__name__).exception("Error in feature_values_by_feature")
        return JsonResponse({"error": "Internal server error"}, status=500)


def with_list_relations(queryset):
    """Everything ProductListSerializer reads, loaded in a fixed number of queries
    instead of several queries per product."""
    return queryset.select_related("category", "brand").prefetch_related("images")


# -------------------------
# ViewSets
# -------------------------


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """Product lists of the whole site go through api/catalog.py (filters, sorting, facets)."""

    queryset = Product.objects.all()
    lookup_field = "slug"
    pagination_class = CatalogPagination

    def get_queryset(self):
        if self.action != "list":
            return with_list_relations(Product.objects.all())
        query = parse_catalog_query(self.request.query_params)
        return with_list_relations(sort_products(filter_products(query), query.sort))

    @action(detail=False, methods=["get"])
    def facets(self, request):
        """Filter groups with counts for the same parameters as the list."""
        return Response(build_facets(parse_catalog_query(request.query_params)))

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ProductDetailSerializer
        return ProductListSerializer


class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    lookup_field = "slug"
    filter_backends = [filters.SearchFilter, BrandFilter]
    search_fields = ["name", "description"]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = Brand.objects.annotate(products_count=Count("products"))
        return queryset


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    # The list shows the root categories (children are nested inside them);
    # detail pages and their actions accept any category, subcategories included.
    queryset = Category.objects.all().order_by("order", "name")
    pagination_class = LargeListPagination  # the frontend shows the whole list, no page switching
    serializer_class = CategorySerializer
    lookup_field = "slug"

    def get_queryset(self):
        queryset = (
            super().get_queryset().annotate(direct_products_count=Count("products", distinct=True))
        )
        if self.action == "list":
            queryset = queryset.filter(parent=None)
            limit = parse_limit(self.request.query_params.get("limit"))
            if limit:
                queryset = queryset[:limit]
        return queryset

    def retrieve(self, request, *args, **kwargs):
        """Detail + `ancestors` (root first) for the breadcrumbs of the category page."""
        response = super().retrieve(request, *args, **kwargs)
        response.data["ancestors"] = category_ancestors(self.get_object())
        return response


class BannerViewSet(viewsets.ReadOnlyModelViewSet):
    """Публичный ViewSet для баннеров"""

    queryset = Banner.objects.filter(is_active=True).order_by("order")
    serializer_class = BannerSerializer
    pagination_class = None


class NewsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NewsItem.objects.filter(is_published=True).order_by("-pub_date")
    lookup_field = "slug"
    pagination_class = LargeListPagination  # the news page lists every published item

    def get_serializer_class(self):
        if self.action == "retrieve":
            return NewsDetailSerializer
        return NewsItemSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        limit = parse_limit(self.request.query_params.get("limit"))
        if limit and self.action == "list":
            queryset = queryset[:limit]
        return queryset


class AboutContentView(generics.RetrieveAPIView):
    serializer_class = AboutContentSerializer

    def get_object(self):
        obj = AboutContent.objects.first()
        if obj is None:
            return AboutContent(title="О нас", content="Информация временно отсутствует")
        return obj


class ContactInfoView(generics.RetrieveAPIView):
    serializer_class = ContactInfoSerializer

    def get_object(self):
        obj = ContactInfo.objects.first()
        if obj is None:
            return ContactInfo(phone="", email="", address="Информация отсутствует")
        return obj


class ContactMessageView(generics.CreateAPIView):
    queryset = ContactMessage.objects.all()
    throttle_classes = PUBLIC_WRITE_THROTTLES
    serializer_class = ContactMessageSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        return Response(
            {"message": "Ваше сообщение успешно отправлено!"}, status=status.HTTP_201_CREATED
        )


# ============ ADMIN VIEWSETS ============


# File upload validation lives in api/uploads.py (content-based, via Pillow).


class ProductAdminViewSet(viewsets.ModelViewSet):
    """CRUD для товаров (админка) с поддержкой inline изображений, характеристик и групп тегов"""

    queryset = Product.objects.all().select_related("category", "brand").order_by("-created_at")
    serializer_class = ProductAdminSerializer
    lookup_field = "pk"
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get("search")
        category = int_param(self.request.query_params, "category")
        brand = int_param(self.request.query_params, "brand")
        is_available = self.request.query_params.get("is_available")

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(internal_sku__icontains=search)
                | Q(manufacturer_sku__icontains=search)
            )
        if category is not None:
            queryset = queryset.filter(category_id=category)
        if brand is not None:
            queryset = queryset.filter(brand_id=brand)
        if is_available is not None:
            queryset = queryset.filter(is_available=is_available.lower() in ["true", "1"])

        return queryset

    # Inline create/update bypass serializer validation; turn bad input into 400, not 500.
    _BAD_INPUT_ERRORS = (
        DjangoValidationError,
        ValueError,
        TypeError,
        IntegrityError,
        DataError,
        ObjectDoesNotExist,
    )

    def create(self, request, *args, **kwargs):
        try:
            return self._create(request, *args, **kwargs)
        except self._BAD_INPUT_ERRORS as exc:
            return Response(
                {"detail": f"Некорректные данные товара: {exc}"}, status=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request, *args, **kwargs):
        try:
            return self._update(request, *args, **kwargs)
        except self._BAD_INPUT_ERRORS as exc:
            return Response(
                {"detail": f"Некорректные данные товара: {exc}"}, status=status.HTTP_400_BAD_REQUEST
            )

    @staticmethod
    def _check_lengths(data):
        # SQLite does not enforce max_length, and this view bypasses the serializer.
        for field in ("name", "manufacturer_sku", "internal_sku"):
            limit = Product._meta.get_field(field).max_length
            if len(str(data.get(field) or "")) > limit:
                raise ValidationError({field: f"Не длиннее {limit} символов."})

    @staticmethod
    def _validated_related(data, product_pk=None) -> list[int] | None:
        """related_ids: existing products other than the product itself; None when not sent."""
        if "related_ids" not in data:
            return None
        raw = data.get("related_ids") or []
        if not isinstance(raw, list) or not all(isinstance(x, int) for x in raw):
            raise ValidationError({"related_ids": "Ожидается список номеров товаров."})
        ids = list(dict.fromkeys(raw))
        if product_pk is not None and product_pk in ids:
            raise ValidationError({"related_ids": "Товар не может быть сопутствующим сам себе."})
        if Product.objects.filter(pk__in=ids).count() != len(ids):
            raise ValidationError({"related_ids": "Некоторые товары не найдены."})
        return ids

    @staticmethod
    def _validated_commerce(data) -> dict:
        """Old price, stock, status and "recommended" from the admin form; only the keys sent."""
        values = {}
        if "old_price" in data:
            values["old_price"] = price_value(data, "old_price")
        if "stock_quantity" in data:
            qty = int_param(data, "stock_quantity")
            if qty is not None and qty < 0:
                raise ValidationError({"stock_quantity": "Количество не может быть меньше 0."})
            values["stock_quantity"] = qty
        if "status" in data:
            status_value = str(data.get("status") or "")
            if status_value and status_value not in Product.STATUS_LABELS:
                raise ValidationError({"status": "Неизвестный ярлык товара."})
            values["status"] = status_value
        if "is_recommended" in data:
            values["is_recommended"] = str(data.get("is_recommended")).lower() in ("true", "1")
        return values

    @staticmethod
    def _validated_name(data):
        name = str(data.get("name") or "").strip()
        if not name:
            raise ValidationError({"name": "Укажите название товара."})
        return name

    @staticmethod
    def _validated_category_id(data):
        category_id = int_param(data, "category")
        if category_id is None:
            raise ValidationError({"category": "Выберите каталог."})
        if not Category.objects.filter(pk=category_id).exists():
            raise ValidationError({"category": "Каталог не найден."})
        return category_id

    @staticmethod
    def _validated_brand_id(data):
        if not data.get("brand"):
            return None
        brand_id = int_param(data, "brand")
        if not Brand.objects.filter(pk=brand_id).exists():
            raise ValidationError({"brand": "Бренд не найден."})
        return brand_id

    @staticmethod
    def _validated_internal_sku(data, exclude_pk=None):
        sku = str(data.get("internal_sku") or "").strip() or None
        if sku and Product.objects.filter(internal_sku=sku).exclude(pk=exclude_pk).exists():
            raise ValidationError(
                {"internal_sku": f"Внутренний SKU «{sku}» уже есть у другого товара."}
            )
        return sku

    def _create(self, request, *args, **kwargs):
        """Создание товара с inline данными"""
        from django.db import transaction

        data = request.data
        self._check_lengths(data)
        name = self._validated_name(data)
        category_id = self._validated_category_id(data)
        price = price_value(data)
        brand_id = self._validated_brand_id(data)
        internal_sku = self._validated_internal_sku(data)
        features_data = inline_list(data, "features")
        related_ids = self._validated_related(data)

        with transaction.atomic():
            # Основные данные товара
            product_data = {
                "name": name,
                # Taken slug (same product name twice) -> kamera-x-2 instead of an error.
                "slug": unique_slug(Product, data.get("slug") or name, 200),
                "description": data.get("description", ""),
                "category_id": category_id,
                "brand_id": brand_id,
                "price": price,
                "is_available": data.get("is_available", True),
                "manufacturer_sku": data.get("manufacturer_sku", ""),
                "internal_sku": internal_sku,
                **self._validated_commerce(data),
            }

            product = Product(**product_data)
            product.save()

            # Обработка характеристик (features)
            for feat in features_data:
                if feat.get("feature_id") and feat.get("value_id"):
                    ProductFeature.objects.create(
                        product=product, feature_id=feat["feature_id"], value_id=feat["value_id"]
                    )
            if related_ids:
                product.related.set(related_ids)

        serializer = self.get_serializer(product)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _update(self, request, *args, **kwargs):
        """Обновление товара с inline данными"""
        from django.db import transaction

        kwargs.pop("partial", False)
        product = self.get_object()
        data = request.data
        self._check_lengths(data)
        name = self._validated_name(data) if "name" in data else product.name
        category_id = (
            self._validated_category_id(data) if "category" in data else product.category_id
        )
        price = price_value(data) if "price" in data else product.price
        commerce = self._validated_commerce(data)
        brand_id = self._validated_brand_id(data) if "brand" in data else product.brand_id
        internal_sku = (
            self._validated_internal_sku(data, product.pk)
            if data.get("internal_sku")
            else product.internal_sku
        )
        features_data = inline_list(data, "features") if "features" in data else None
        related_ids = self._validated_related(data, product.pk)
        images_data = inline_list(data, "images") if "images" in data else None

        with transaction.atomic():
            # Обновляем основные поля товара
            product.name = name
            if data.get("slug") and data["slug"] != product.slug:
                new_slug = make_slug(data["slug"], 200)
                if Product.objects.filter(slug=new_slug).exclude(pk=product.pk).exists():
                    raise ValidationError(
                        {"slug": f"Адрес (slug) «{new_slug}» уже занят другим товаром."}
                    )
                product.slug = new_slug
            product.description = data.get("description", product.description)
            product.category_id = category_id
            product.brand_id = brand_id
            product.price = price
            if "is_available" in data:
                product.is_available = data["is_available"]
            if "manufacturer_sku" in data:
                product.manufacturer_sku = data["manufacturer_sku"] or ""
            product.internal_sku = internal_sku
            for field, value in commerce.items():
                setattr(product, field, value)
            product.save()

            # Обновляем характеристики
            if features_data is not None:
                product.features.all().delete()
                for feat in features_data:
                    if feat.get("feature_id") and feat.get("value_id"):
                        ProductFeature.objects.create(
                            product=product,
                            feature_id=feat["feature_id"],
                            value_id=feat["value_id"],
                        )

            # Обновляем изображения (порядок и is_main)
            if images_data is not None:
                for img_data in images_data:
                    if img_data.get("id"):
                        try:
                            img = Image.objects.get(id=img_data["id"], product=product)
                            if "is_main" in img_data:
                                img.is_main = img_data["is_main"]
                            if "order" in img_data:
                                img.order = img_data["order"]
                            if img_data.get("_delete"):
                                img.delete()
                            else:
                                img.save()
                        except Image.DoesNotExist:
                            pass

            if related_ids is not None:
                product.related.set(related_ids)

        serializer = self.get_serializer(product)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="upload-image")
    def upload_image(self, request, pk=None):
        product = self.get_object()
        files = request.FILES.getlist("images")
        if not files:
            file = request.FILES.get("image")
            if file:
                files = [file]

        if not files:
            return Response({"error": "No images provided"}, status=400)

        # Validate the whole batch first: a bad file must not leave half of it saved.
        for f in files:
            is_valid, error_msg = validate_uploaded_image(f)
            if not is_valid:
                return Response({"error": error_msg}, status=400)
        # Optional form fields sent by the admin product form for a single new photo:
        # is_main (the admin ticked "Главное" on it) and order (its place in the list).
        make_main = str(request.data.get("is_main", "")).lower() in ("true", "1")
        order = int_param(request.data, "order")  # 400 on a non-number
        from django.db import transaction

        uploaded = []
        with transaction.atomic():
            if make_main:
                product.images.update(is_main=False)
            for i, f in enumerate(files):
                img = Image.objects.create(
                    product=product,
                    image=f,
                    is_main=make_main and i == 0,
                    order=order if order is not None else 0,
                )
                uploaded.append({"id": img.id, "image": img.image.url if img.image else None})

        return Response({"images": uploaded}, status=201)

    @action(detail=True, methods=["post"], url_path="documents")
    def upload_document(self, request, pk=None):
        """A file for the "Документация" tab: title + file (PDF, Word, Excel, archive)."""
        product = self.get_object()
        title = str(request.data.get("title") or "").strip()
        file = request.FILES.get("file")
        if not title or len(title) > 200:
            return Response(
                {"title": ["Укажите название документа (до 200 символов)."]}, status=400
            )
        if file is None:
            return Response({"file": ["Выберите файл."]}, status=400)
        ok, error = validate_uploaded_document(file)
        if not ok:
            return Response({"file": [error]}, status=400)
        order = product.documents.count()
        doc = ProductDocument.objects.create(product=product, title=title, file=file, order=order)
        return Response(ProductDocumentSerializer(doc).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["delete"], url_path="documents/(?P<doc_id>[0-9]+)")
    def delete_document(self, request, pk=None, doc_id=None):
        product = self.get_object()
        deleted, _ = ProductDocument.objects.filter(product=product, pk=doc_id).delete()
        if not deleted:
            return Response({"detail": "Документ не найден."}, status=404)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["delete"], url_path="delete-image/(?P<image_id>[0-9]+)")
    def delete_image(self, request, pk=None, image_id=None):
        product = self.get_object()
        try:
            img = Image.objects.get(id=image_id, product=product)
            img.delete()
            return Response({"success": True})
        except Image.DoesNotExist:
            return Response({"error": "Image not found"}, status=404)


def plural_ru(n, one, few, many):
    """1 товар, 2 товара, 5 товаров."""
    if n % 10 == 1 and n % 100 != 11:
        return f"{n} {one}"
    if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14:
        return f"{n} {few}"
    return f"{n} {many}"


class ProtectedDeleteMixin:
    """DELETE of an object that others still depend on (on_delete=PROTECT) answers
    400 with an explanation for the admin instead of a 500."""

    def protected_delete_message(self, obj):
        raise NotImplementedError

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {"detail": self.protected_delete_message(self.get_object())},
                status=status.HTTP_400_BAD_REQUEST,
            )


class CategoryAdminViewSet(ProtectedDeleteMixin, viewsets.ModelViewSet):
    """CRUD для категорий (админка)"""

    queryset = Category.objects.all().order_by("order", "name")
    pagination_class = LargeListPagination  # the frontend shows the whole list, no page switching
    serializer_class = CategoryAdminSerializer
    lookup_field = "pk"
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get("search")
        parent = self.request.query_params.get("parent")

        if search:
            queryset = queryset.filter(name__icontains=search)
        if parent:
            if parent == "null":
                queryset = queryset.filter(parent__isnull=True)
            else:
                queryset = queryset.filter(parent_id=int_param(self.request.query_params, "parent"))

        return queryset

    def protected_delete_message(self, category):
        parts = []
        products = category.products.count()
        children = category.children.count()
        if products:
            parts.append(plural_ru(products, "товар", "товара", "товаров"))
        if children:
            parts.append(plural_ru(children, "подкаталог", "подкаталога", "подкаталогов"))
        return (
            f"Нельзя удалить каталог «{category.name}»: в нём {' и '.join(parts)}. "
            "Сначала перенесите их в другой каталог или удалите."
        )

    @action(detail=True, methods=["post"], url_path="upload-image")
    def upload_image(self, request, pk=None):
        category = self.get_object()
        image = request.FILES.get("image")
        if image:
            is_valid, error_msg = validate_uploaded_image(image)
            if not is_valid:
                return Response({"error": error_msg}, status=400)
            category.image = image
            category.save()
            return Response({"image": category.image.url if category.image else None})
        return Response({"error": "No image provided"}, status=400)

    @action(detail=True, methods=["delete"], url_path="delete-image")
    def delete_image(self, request, pk=None):
        category = self.get_object()
        if category.image:
            category.image.delete(save=False)
            category.image = None
            category.save()
        return Response({"image": None})


class BrandAdminViewSet(ProtectedDeleteMixin, viewsets.ModelViewSet):
    """CRUD для брендов (админка)"""

    def protected_delete_message(self, brand):
        count = plural_ru(brand.products.count(), "товар", "товара", "товаров")
        return (
            f"Нельзя удалить бренд «{brand.name}»: к нему привязано {count}. "
            "Сначала смените бренд у этих товаров или удалите их."
        )

    queryset = Brand.objects.all().order_by("name")
    pagination_class = LargeListPagination  # the frontend shows the whole list, no page switching
    serializer_class = BrandAdminSerializer
    lookup_field = "pk"
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(description__icontains=search))
        return queryset

    @action(detail=True, methods=["post"], url_path="upload-logo")
    def upload_logo(self, request, pk=None):
        brand = self.get_object()
        logo = request.FILES.get("logo")
        if logo:
            is_valid, error_msg = validate_uploaded_image(logo)
            if not is_valid:
                return Response({"error": error_msg}, status=400)
            brand.logo = logo
            brand.save()
            return Response({"logo": brand.logo.url if brand.logo else None})
        return Response({"error": "No logo provided"}, status=400)


class FeatureAdminViewSet(viewsets.ModelViewSet):
    """CRUD для характеристик (админка)"""

    queryset = (
        Feature.objects.select_related("category").prefetch_related("values").order_by("name")
    )
    serializer_class = FeatureAdminSerializer
    lookup_field = "pk"
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get("search")
        category = int_param(self.request.query_params, "category")

        if search:
            queryset = queryset.filter(name__icontains=search)
        if category is not None:
            queryset = queryset.filter(category_id=category)

        return queryset


class FeatureValueAdminViewSet(viewsets.ModelViewSet):
    """CRUD для значений характеристик (админка)"""

    queryset = (
        FeatureValue.objects.select_related("category")
        .prefetch_related("features")
        .order_by("value")
    )
    serializer_class = FeatureValueAdminSerializer
    lookup_field = "pk"
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get("search")
        category = int_param(self.request.query_params, "category")
        feature = int_param(self.request.query_params, "feature")

        if search:
            queryset = queryset.filter(value__icontains=search)
        if category is not None:
            queryset = queryset.filter(category_id=category)
        if feature is not None:
            # Фильтруем значения, привязанные к указанной характеристике
            queryset = queryset.filter(features__id=feature).distinct()

        return queryset


class NewsAdminViewSet(viewsets.ModelViewSet):
    """CRUD для новостей (админка)"""

    queryset = NewsItem.objects.all().order_by("-pub_date")
    pagination_class = LargeListPagination  # the frontend shows the whole list, no page switching
    serializer_class = NewsAdminSerializer
    lookup_field = "pk"
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get("search")
        is_published = self.request.query_params.get("is_published")

        if search:
            queryset = queryset.filter(Q(title__icontains=search) | Q(content__icontains=search))
        if is_published is not None:
            queryset = queryset.filter(is_published=is_published.lower() == "true")

        return queryset


class ImageAdminViewSet(viewsets.ModelViewSet):
    """CRUD для изображений товаров (админка)"""

    queryset = Image.objects.all().order_by("order")
    pagination_class = LargeListPagination  # the frontend shows the whole list, no page switching
    serializer_class = ImageAdminSerializer
    lookup_field = "pk"
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = super().get_queryset()
        product = int_param(self.request.query_params, "product")
        if product is not None:
            queryset = queryset.filter(product_id=product)
        return queryset


class AboutContentAdminView(generics.RetrieveUpdateAPIView):
    """Получение и обновление страницы О нас"""

    serializer_class = AboutContentAdminSerializer
    permission_classes = [IsAdminUser]

    def get_object(self):
        from django.db import transaction as db_transaction

        with db_transaction.atomic():
            obj = AboutContent.objects.select_for_update().first()
            if not obj:
                obj = AboutContent.objects.create(title="О нас", content="")
        return obj


class ContactInfoAdminView(generics.RetrieveUpdateAPIView):
    """Получение и обновление контактной информации"""

    serializer_class = ContactInfoAdminSerializer
    permission_classes = [IsAdminUser]

    def get_object(self):
        from django.db import transaction as db_transaction

        with db_transaction.atomic():
            obj = ContactInfo.objects.select_for_update().first()
            if not obj:
                obj = ContactInfo.objects.create(phone="", email="", address="")
        return obj


class ContactMessageAdminViewSet(viewsets.ModelViewSet):
    """Управление сообщениями от посетителей"""

    queryset = ContactMessage.objects.all().order_by("-created_at")
    pagination_class = LargeListPagination  # the frontend shows the whole list, no page switching
    serializer_class = ContactMessageAdminSerializer
    permission_classes = [IsAdminUser]
    lookup_field = "pk"

    def get_queryset(self):
        queryset = super().get_queryset()
        is_processed = self.request.query_params.get("is_processed")

        if is_processed is not None:
            queryset = queryset.filter(is_processed=is_processed.lower() == "true")

        return queryset

    @action(detail=True, methods=["post"], url_path="mark-processed")
    def mark_processed(self, request, pk=None):
        message = self.get_object()
        message.is_processed = True
        message.save()
        return Response({"status": "processed", "id": message.id})

    @action(detail=True, methods=["post"], url_path="mark-unprocessed")
    def mark_unprocessed(self, request, pk=None):
        message = self.get_object()
        message.is_processed = False
        message.save()
        return Response({"status": "unprocessed", "id": message.id})


# ============ AUTH VIEWS ============


# ============ BANNER ADMIN VIEWSET ============
class BannerAdminViewSet(viewsets.ModelViewSet):
    """Admin ViewSet для управления баннерами"""

    queryset = Banner.objects.all().order_by("order")
    serializer_class = BannerSerializer
    permission_classes = [IsAdminUser]
    pagination_class = None

    def update(self, request, *args, **kwargs):

        # Если явно передан image: null, удаляем старое изображение
        if "image" in request.data and request.data["image"] is None:
            banner = self.get_object()
            if banner.image:
                banner.image.delete(save=False)
            banner.image = None
            banner.save()

        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=["post"], url_path="upload-image")
    def upload_image(self, request, pk=None):
        """Загрузка изображения для баннера"""
        banner = self.get_object()
        image = request.FILES.get("image")

        if not image:
            return Response({"error": "No image provided"}, status=status.HTTP_400_BAD_REQUEST)

        is_valid, error_msg = validate_uploaded_image(image)
        if not is_valid:
            return Response({"error": error_msg}, status=status.HTTP_400_BAD_REQUEST)

        banner.image = image
        banner.save()

        serializer = self.get_serializer(banner)
        return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def admin_change_password(request):
    """Смена пароля для админов (JWT совместимая версия)"""
    if not request.user.is_staff:
        return Response(
            {"detail": "Only admin users can access this endpoint."},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = ChangePasswordSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user = request.user
    if not user.check_password(serializer.validated_data["old_password"]):
        return Response({"error": "Неверный текущий пароль"}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(serializer.validated_data["new_password"])
    user.save()

    # Sign out every other session; the current one continues with a fresh pair.
    revoke_all_refresh_tokens(user)
    new_refresh = RefreshToken.for_user(user)
    return Response(
        {
            "message": "Пароль успешно изменен",
            "access": str(new_refresh.access_token),
            "refresh": str(new_refresh),
        }
    )


@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def admin_update_profile(request):
    """Обновление профиля админа (JWT совместимая версия)"""
    if not request.user.is_staff:
        return Response(
            {"detail": "Only admin users can access this endpoint."},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = UpdateProfileSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(UserSerializer(request.user).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============ DASHBOARD STATS ============


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_stats(request):
    """Статистика для Dashboard (JWT совместимая версия)"""
    if not request.user.is_staff:
        return Response(
            {"detail": "Only admin users can access this endpoint."},
            status=status.HTTP_403_FORBIDDEN,
        )

    stats = {
        "products_count": Product.objects.count(),
        "categories_count": Category.objects.count(),
        "brands_count": Brand.objects.count(),
        "news_count": NewsItem.objects.count(),
        "published_news_count": NewsItem.objects.filter(is_published=True).count(),
        "unread_messages": ContactMessage.objects.filter(is_processed=False).count(),
        "total_messages": ContactMessage.objects.count(),
        "available_products": Product.objects.filter(is_available=True).count(),
        "features_count": Feature.objects.count(),
        "orders_count": Order.objects.count(),
        "new_orders_count": Order.objects.filter(status="new").count(),
    }
    return Response(stats)


# ============ ORDERS ============


class OrderViewSet(viewsets.ModelViewSet):
    """Публичный endpoint для создания заказов.
    Только POST (create) разрешён анонимным пользователям.
    GET/PATCH/DELETE требуют авторизации (только для админа).
    """

    queryset = Order.objects.prefetch_related("items").order_by("-created_at")
    throttle_classes = ORDER_THROTTLES

    def get_serializer_class(self):
        if self.request.user and self.request.user.is_staff:
            return OrderAdminSerializer
        return OrderSerializer

    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]
        return [IsAdminUser()]

    def get_queryset(self):
        return filter_orders(
            Order.objects.prefetch_related("items").order_by("-created_at"),
            self.request.query_params,
        )


def filter_orders(qs, params):
    """Order list filters shared by the admin list and the CSV export:
    search, status, date_from, date_to (YYYY-MM-DD; anything else -> 400)."""
    search = params.get("search", "").strip()
    status_filter = params.get("status", "").strip()
    date_from = date_param(params, "date_from")
    date_to = date_param(params, "date_to")
    if search:
        qs = qs.filter(
            Q(customer_name__icontains=search)
            | Q(customer_phone__icontains=search)
            | Q(customer_email__icontains=search)
        )
    if status_filter:
        qs = qs.filter(status=status_filter)
    if date_from:
        qs = qs.filter(created_at__date__gte=date_from)
    if date_to:
        qs = qs.filter(created_at__date__lte=date_to)
    return qs


@api_view(["GET"])
@permission_classes([IsAdminUser])
def export_orders_csv(request):
    """Экспорт заявок в CSV с фильтрами: search, status, date_from, date_to."""
    qs = filter_orders(
        Order.objects.prefetch_related("items").order_by("-created_at"), request.query_params
    )

    STATUS_MAP = {
        "new": "Новый",
        "processing": "В обработке",
        "completed": "Выполнен",
        "cancelled": "Отменён",
        "wrong_phone": "Неправильный номер",
        "no_answer": "Не поднял трубку",
    }

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="orders_export.csv"'
    response.write("\ufeff")  # BOM for Excel UTF-8

    writer = csv.writer(response)
    writer.writerow(
        [
            "#",
            "Дата",
            "Имя",
            "Телефон",
            "Email",
            "Telegram",
            "Статус",
            "Комментарий",
            "Товары",
            "Сумма",
        ]
    )

    for order in qs:
        items_str = "; ".join(
            f"{i.product_name} x{i.quantity}" + (f" ({i.price} сум)" if i.price else "")
            for i in order.items.all()
        )
        total = sum((i.price or 0) * i.quantity for i in order.items.all())
        # Every cell goes through safe_csv_cell: customer input must not run as a formula.
        writer.writerow(
            [
                safe_csv_cell(cell)
                for cell in [
                    order.id,
                    order.created_at.strftime("%d.%m.%Y %H:%M"),
                    order.customer_name,
                    order.customer_phone,
                    order.customer_email or "—",
                    order.customer_telegram or "—",
                    STATUS_MAP.get(order.status, order.status),
                    order.comment or "—",
                    items_str or "—",
                    f"{total:,.0f}" if total else "—",
                ]
            ]
        )

    return response


# ============ REVIEWS & QUESTIONS ============


class ProductReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ProductReviewSerializer
    throttle_classes = PUBLIC_WRITE_THROTTLES
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        product_slug = self.kwargs.get("product_slug")
        return ProductReview.objects.filter(product__slug=product_slug, is_published=True).order_by(
            "-created_at"
        )

    def get_permissions(self):
        if self.action in ("list", "retrieve", "create"):
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        # New public submissions wait for moderation in the admin panel.
        product = get_object_or_404(Product, slug=self.kwargs.get("product_slug"))
        serializer.save(product=product, is_published=False)


class ProductQuestionViewSet(viewsets.ModelViewSet):
    serializer_class = ProductQuestionSerializer
    throttle_classes = PUBLIC_WRITE_THROTTLES
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        product_slug = self.kwargs.get("product_slug")
        return ProductQuestion.objects.filter(
            product__slug=product_slug, is_published=True
        ).order_by("-created_at")

    def get_permissions(self):
        if self.action in ("list", "retrieve", "create"):
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        # New public submissions wait for moderation in the admin panel.
        product = get_object_or_404(Product, slug=self.kwargs.get("product_slug"))
        serializer.save(product=product, is_published=False)


@api_view(["GET"])
def similar_products(request, slug):
    """
    Similarity Score Algorithm (e-commerce standard):
    Hard filters: same category, exclude self.
    Scoring:
      +3  same brand
      +2  price within ±20% of current product price
      +1  per matching feature value (ProductFeature.value_id)
    Products with 0 points are excluded.
    Sorted by score desc, limited to top 6.
    """
    try:
        product = Product.objects.select_related("category", "brand").get(slug=slug)
    except Product.DoesNotExist:
        return Response({"detail": "Not found"}, status=404)

    # -- Collect current product's feature value IDs for attribute matching --
    current_value_ids = set(
        ProductFeature.objects.filter(product=product, value__isnull=False).values_list(
            "value_id", flat=True
        )
    )

    # -- Strict base filter: same category, available, not self --
    candidates = (
        Product.objects.filter(category=product.category, is_available=True)
        .exclude(id=product.id)
        .select_related("category", "brand")
        .prefetch_related("images", "features")
    )

    # -- Price bounds for ±20% check --
    price_lower = price_upper = None
    if product.price is not None:
        price_lower = product.price * Decimal("0.80")
        price_upper = product.price * Decimal("1.20")

    scored = []
    for candidate in candidates:
        score = 0

        # +3 — brand match
        if product.brand_id and candidate.brand_id == product.brand_id:
            score += 3

        # +2 — price proximity ±20%
        if price_lower is not None and candidate.price is not None:
            if price_lower <= candidate.price <= price_upper:
                score += 2

        # +1 per matching feature value
        if current_value_ids:
            candidate_value_ids = set(
                pf.value_id for pf in candidate.features.all() if pf.value_id is not None
            )
            score += len(current_value_ids & candidate_value_ids)

        if score > 0:
            scored.append((score, candidate))

    # Sort by score descending, take top 6
    scored.sort(key=lambda x: x[0], reverse=True)
    top_products = [p for _, p in scored[:6]]

    serializer = ProductListSerializer(top_products, many=True, context={"request": request})
    return Response(serializer.data)


# ============ ADMIN: REVIEWS & QUESTIONS ============


class ReviewAdminViewSet(viewsets.ModelViewSet):
    """Управление отзывами о товарах"""

    queryset = ProductReview.objects.select_related("product").order_by("-created_at")
    pagination_class = LargeListPagination  # the frontend shows the whole list, no page switching
    serializer_class = ProductReviewAdminSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = super().get_queryset()
        is_published = self.request.query_params.get("is_published")
        product = int_param(self.request.query_params, "product")
        rating = int_param(self.request.query_params, "rating")
        search = self.request.query_params.get("search")
        if is_published is not None:
            queryset = queryset.filter(is_published=is_published.lower() == "true")
        if product is not None:
            queryset = queryset.filter(product_id=product)
        if rating is not None:
            queryset = queryset.filter(rating=rating)
        if search:
            queryset = queryset.filter(Q(author_name__icontains=search) | Q(text__icontains=search))
        return queryset

    def perform_update(self, serializer):
        from django.utils import timezone

        instance = serializer.save()
        if instance.admin_reply and not instance.admin_reply_date:
            instance.admin_reply_date = timezone.now()
            instance.save()


class QuestionAdminViewSet(viewsets.ModelViewSet):
    """Управление вопросами о товарах"""

    queryset = ProductQuestion.objects.select_related("product").order_by("-created_at")
    pagination_class = LargeListPagination  # the frontend shows the whole list, no page switching
    serializer_class = ProductQuestionAdminSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = super().get_queryset()
        is_published = self.request.query_params.get("is_published")
        product = int_param(self.request.query_params, "product")
        search = self.request.query_params.get("search")
        if is_published is not None:
            queryset = queryset.filter(is_published=is_published.lower() == "true")
        if product is not None:
            queryset = queryset.filter(product_id=product)
        if search:
            queryset = queryset.filter(Q(author_name__icontains=search) | Q(text__icontains=search))
        return queryset

    def perform_update(self, serializer):
        from django.utils import timezone

        instance = serializer.save()
        if instance.admin_reply and not instance.admin_reply_date:
            instance.admin_reply_date = timezone.now()
            instance.save()


# ============ PAGES FOR BUYERS ============


class InfoPageViewSet(viewsets.ReadOnlyModelViewSet):
    """Published pages: the list (slug, title) feeds the footer, the detail is the page."""

    queryset = InfoPage.objects.filter(is_published=True).order_by("order", "title")
    lookup_field = "slug"
    pagination_class = None

    def get_serializer_class(self):
        return InfoPageSerializer if self.action == "retrieve" else InfoPageListSerializer


class InfoPageAdminViewSet(viewsets.ModelViewSet):
    queryset = InfoPage.objects.all().order_by("order", "title")
    serializer_class = InfoPageAdminSerializer
    pagination_class = LargeListPagination
    permission_classes = [IsAdminUser]
