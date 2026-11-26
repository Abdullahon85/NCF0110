# models.py

from django.db import models

from .slugs import unique_slug


class Category(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название")
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    # PROTECT: a category with subcategories cannot be deleted (they would vanish with it).
    parent = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="Родительская категория",
    )
    image = models.ImageField(
        upload_to="categories/", blank=True, null=True, verbose_name="Изображение"
    )
    order = models.IntegerField(default=0, verbose_name="Порядок сортировки")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["order", "name"]

    def clean(self):
        # Same rule as the admin API (CategoryAdminSerializer.validate_parent),
        # for the optional stock Django admin.
        from django.core.exceptions import ValidationError

        from .categories import is_self_or_descendant

        if self.pk and self.parent_id and is_self_or_descendant(self.parent_id, self.pk):
            raise ValidationError(
                {"parent": "Нельзя выбрать родителем сам каталог или его подкаталог."}
            )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(Category, self.name, 200, self.pk)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_all_products(self):
        """Все товары каталога, включая подкаталоги любой глубины (безопасно при цикле)."""
        from .categories import subtree_ids

        return (
            Product.objects.filter(category_id__in=subtree_ids([self.id]))
            .select_related("category", "brand")
            .prefetch_related("images")
        )


class Brand(models.Model):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=160, unique=True, blank=True)
    logo = models.ImageField(upload_to="brands/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)  # 👈 добавь

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(Brand, self.name, 160, self.pk)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название")
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    brand = models.ForeignKey(
        Brand, on_delete=models.PROTECT, null=True, blank=True, related_name="products"
    )
    description = models.TextField(verbose_name="Описание")
    # PROTECT: deleting a category must never silently delete its products.
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="products", verbose_name="Категория"
    )
    price = models.DecimalField(
        max_digits=25, decimal_places=2, null=True, blank=True, verbose_name="Цена"
    )
    is_available = models.BooleanField(default=True, verbose_name="В наличии")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    manufacturer_sku = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Артикул производителя"
    )
    internal_sku = models.CharField(
        max_length=100, unique=True, blank=True, null=True, verbose_name="Внутренний SKU"
    )
    # Struck-through price next to the current one; the discount is computed (api/pricing.py).
    old_price = models.DecimalField(
        max_digits=25, decimal_places=2, null=True, blank=True, verbose_name="Старая цена"
    )
    # None = not specified ("В наличии" without a number).
    stock_quantity = models.PositiveIntegerField(null=True, blank=True, verbose_name="Количество")
    STATUS_LABELS = {"new": "Новинка", "promo": "Акция", "sale": "Распродажа"}
    status = models.CharField(
        max_length=10,
        blank=True,
        default="",
        choices=[("", "Нет"), *STATUS_LABELS.items()],
        verbose_name="Ярлык",
    )
    is_recommended = models.BooleanField(default=False, verbose_name="Рекомендуем")
    # "Сопутствующие товары" tab: chosen by the admin, one direction only.
    related = models.ManyToManyField(
        "self",
        symmetrical=False,
        blank=True,
        related_name="related_to",
        verbose_name="Сопутствующие товары",
    )

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(Product, self.name, 200, self.pk)
        super().save(*args, **kwargs)
        if not self.internal_sku:
            # Prefix from the category slug (or the name) + the product number: KAM-00042.
            raw_prefix = self.category.slug if self.category.slug else self.name[:3]
            prefix = "".join(ch for ch in raw_prefix.upper() if ch.isalnum())[:3] or "PRD"
            candidate, n = f"{prefix}-{self.pk:05d}", 2
            while Product.objects.filter(internal_sku=candidate).exists():
                candidate, n = f"{prefix}-{self.pk:05d}-{n}", n + 1
            self.internal_sku = candidate
            super().save(update_fields=["internal_sku"])

    def __str__(self):
        return self.name


class FeatureValue(models.Model):
    """Модель для значений характеристик"""

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="feature_values",
        verbose_name="Категория",
        null=True,
        blank=True,
    )
    value = models.CharField(max_length=500, verbose_name="Значение")
    # The number inside `value` (api/numbers.py), used by range filters; None if there is none.
    number = models.DecimalField(max_digits=24, decimal_places=4, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Значение характеристики"
        verbose_name_plural = "Значения характеристик"
        unique_together = ["category", "value"]  # Уникальность в рамках категории
        ordering = ["value"]

    def save(self, *args, **kwargs):
        from .numbers import parse_number

        self.number = parse_number(self.value)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.value


class Feature(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название характеристики")
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="feature", verbose_name="Категория"
    )
    values = models.ManyToManyField(
        FeatureValue, related_name="features", blank=True, verbose_name="Значения"
    )
    # Heading of the characteristics table on the product page ("Общие" when empty).
    group = models.CharField(max_length=100, blank=True, verbose_name="Группа")
    order = models.IntegerField(default=0, verbose_name="Порядок")
    FILTER_TYPES = [
        ("list", "Список"),
        ("bool", "Да/Нет"),
        ("range", "Диапазон"),
        ("none", "Не показывать"),
    ]
    filter_type = models.CharField(
        max_length=10, choices=FILTER_TYPES, default="list", verbose_name="Вид в фильтре"
    )
    unit = models.CharField(max_length=20, blank=True, verbose_name="Единица")

    class Meta:
        verbose_name = "Характеристика"
        verbose_name_plural = "Характеристики"
        unique_together = [["name", "category"]]  # Уникальность в рамках категории

    def __str__(self):
        return f"{self.name} ({self.category.name})"


class ProductFeature(models.Model):
    product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE,
        related_name="features",  # оставляем как было
        verbose_name="Товар",
    )
    feature = models.ForeignKey(
        Feature,
        on_delete=models.CASCADE,
        related_name="product_features",  # <- ОБЯЗАТЕЛЬНО уникальное имя
        verbose_name="Характеристика",
        null=True,
        blank=True,
    )
    value = models.ForeignKey(
        FeatureValue,
        on_delete=models.CASCADE,
        verbose_name="Значение",
        null=True,
        blank=True,
        related_name="product_features",
    )

    class Meta:
        verbose_name = "Характеристика товара"
        verbose_name_plural = "Характеристики товаров"

    def __str__(self):
        return (
            f"{self.feature.name if self.feature else 'N/A'}: {self.value if self.value else 'N/A'}"
        )


class Image(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images", verbose_name="Товар"
    )
    image = models.ImageField(
        upload_to="products/", blank=True, null=True, verbose_name="Изображение"
    )
    is_main = models.BooleanField(default=False, verbose_name="Главное изображение")
    order = models.IntegerField(default=0, verbose_name="Порядок")

    class Meta:
        verbose_name = "Изображение товара"
        verbose_name_plural = "Изображения товаров"
        ordering = ["order"]

    def __str__(self):
        return f"Изображение для {self.product.name}"


class ProductDocument(models.Model):
    """File on the "Документация" tab of the product page (validated in api/documents.py)."""

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="documents", verbose_name="Товар"
    )
    title = models.CharField(max_length=200, verbose_name="Название")
    file = models.FileField(upload_to="documents/", verbose_name="Файл")
    order = models.IntegerField(default=0, verbose_name="Порядок")

    class Meta:
        verbose_name = "Документ товара"
        verbose_name_plural = "Документы товаров"
        ordering = ["order", "id"]

    def __str__(self):
        return self.title


class InfoPage(models.Model):
    """Page for buyers (Оплата, Доставка, Возврат, Гарантия, FAQ): footer column "Покупателям"."""

    title = models.CharField(max_length=200, verbose_name="Заголовок")
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    content = models.TextField(blank=True, verbose_name="Текст")
    order = models.IntegerField(default=0, verbose_name="Порядок")
    is_published = models.BooleanField(default=True, verbose_name="Опубликована")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Страница для покупателей"
        verbose_name_plural = "Страницы для покупателей"
        ordering = ["order", "title"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(InfoPage, self.title, 200, self.pk)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class NewsItem(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    content = models.TextField(verbose_name="Содержание")
    preview = models.TextField(max_length=500, verbose_name="Краткое описание")
    image = models.URLField(blank=True, verbose_name="Ссылка на изображение")
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата публикации")
    is_published = models.BooleanField(default=True, verbose_name="Опубликовано")

    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"
        ordering = ["-pub_date"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(NewsItem, self.title, 200, self.pk)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class AboutContent(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Содержание")
    image = models.URLField(blank=True, verbose_name="Ссылка на изображение")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Страница "О нас"'
        verbose_name_plural = 'Страница "О нас"'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.pk and AboutContent.objects.exists():
            raise ValueError("Может существовать только одна запись AboutContent")
        super().save(*args, **kwargs)


class ContactInfo(models.Model):
    phone = models.CharField(max_length=50, verbose_name="Телефон")
    email = models.EmailField(verbose_name="Email")
    address = models.TextField(verbose_name="Адрес")
    map_url = models.URLField(blank=True, null=True, verbose_name="Ссылка на карту")
    instagram = models.URLField(blank=True, null=True, verbose_name="Instagram")
    telegram = models.URLField(blank=True, null=True, verbose_name="Telegram")
    whatsapp = models.URLField(blank=True, null=True, verbose_name="WhatsApp")
    facebook = models.URLField(blank=True, null=True, verbose_name="Facebook")
    working_hours = models.CharField(
        max_length=200, blank=True, default="Пн-Пт: 9:00-18:00", verbose_name="Режим работы"
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Контактная информация"
        verbose_name_plural = "Контактная информация"

    def __str__(self):
        return "Контактная информация"

    def save(self, *args, **kwargs):
        if not self.pk and ContactInfo.objects.exists():
            raise ValueError("Может существовать только одна запись ContactInfo")
        super().save(*args, **kwargs)


class ContactMessage(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя")
    email = models.EmailField(verbose_name="Email")
    message = models.TextField(verbose_name="Сообщение")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата отправки")
    is_processed = models.BooleanField(default=False, verbose_name="Обработано")

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Сообщение от {self.name} ({self.created_at.strftime('%d.%m.%Y')})"


class Order(models.Model):
    STATUS_CHOICES = [
        ("new", "Новый"),
        ("processing", "В обработке"),
        ("completed", "Выполнен"),
        ("cancelled", "Отменён"),
        ("wrong_phone", "Неправильный номер телефона"),
        ("no_answer", "Не поднял трубку"),
    ]
    customer_name = models.CharField(max_length=150, verbose_name="Имя заказчика")
    customer_phone = models.CharField(max_length=50, verbose_name="Телефон")
    customer_email = models.EmailField(blank=True, verbose_name="Email")
    customer_telegram = models.CharField(max_length=100, blank=True, verbose_name="Telegram")
    comment = models.TextField(blank=True, verbose_name="Комментарий")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="new", verbose_name="Статус"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Заказ #{self.pk} от {self.customer_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items", verbose_name="Заказ"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_items",
        verbose_name="Товар",
    )
    product_name = models.CharField(max_length=200, verbose_name="Название товара")
    product_sku = models.CharField(max_length=100, blank=True, verbose_name="Артикул")
    price = models.DecimalField(
        max_digits=25, decimal_places=2, null=True, blank=True, verbose_name="Цена"
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"

    def __str__(self):
        return f"{self.product_name} x{self.quantity}"


class Banner(models.Model):
    """Баннер для слайдера на главной странице"""

    title = models.CharField(max_length=200, blank=True, null=True, verbose_name="Заголовок")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    image = models.ImageField(
        upload_to="banners/", blank=True, null=True, verbose_name="Изображение"
    )
    link = models.CharField(max_length=500, blank=True, null=True, verbose_name="Ссылка")
    order = models.IntegerField(default=0, verbose_name="Порядок сортировки")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Баннер"
        verbose_name_plural = "Баннеры"
        ordering = ["order", "-created_at"]

    def __str__(self):
        return self.title or f"Баннер #{self.pk}"


class ProductReview(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews", verbose_name="Товар"
    )
    author_name = models.CharField(max_length=150, verbose_name="Имя автора")
    rating = models.PositiveSmallIntegerField(
        verbose_name="Оценка", choices=[(i, str(i)) for i in range(1, 6)]
    )
    text = models.TextField(verbose_name="Текст отзыва")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата")
    is_published = models.BooleanField(default=True, verbose_name="Опубликован")
    admin_reply = models.TextField(blank=True, verbose_name="Ответ администратора")
    admin_reply_date = models.DateTimeField(null=True, blank=True, verbose_name="Дата ответа")

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Отзыв от {self.author_name} на {self.product.name}"


class ProductQuestion(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="questions", verbose_name="Товар"
    )
    author_name = models.CharField(max_length=150, verbose_name="Имя автора")
    text = models.TextField(verbose_name="Текст вопроса")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата")
    is_published = models.BooleanField(default=True, verbose_name="Опубликован")
    admin_reply = models.TextField(blank=True, verbose_name="Ответ администратора")
    admin_reply_date = models.DateTimeField(null=True, blank=True, verbose_name="Дата ответа")

    class Meta:
        verbose_name = "Вопрос о товаре"
        verbose_name_plural = "Вопросы о товарах"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Вопрос от {self.author_name} о {self.product.name}"
