from collections import defaultdict, namedtuple
from typing import Dict, List, Tuple

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import F, Sum
from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItemQuerySet(models.QuerySet):
    def get_available_menu_items(self, products_ids):
        return self.filter(availability=True)\
            .select_related('restaurant')\
            .values(
            'restaurant',
            'restaurant__name',
            'restaurant__address',
            'product'
        ).filter(product__id__in=products_ids)


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    objects = RestaurantMenuItemQuerySet.as_manager()

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"

    @staticmethod
    def get_restaurants_menus(
        menu_items: models.QuerySet
    ) -> Tuple[defaultdict, Dict]:
        restaurants = {}
        menus = defaultdict(list)
        for menu_item in menu_items:
            menus[menu_item['restaurant']].append(menu_item['product'])
            restaurants[menu_item['restaurant']] = {
                'name': menu_item['restaurant__name'],
                'address': menu_item['restaurant__address']
            }

        return menus, restaurants


class OrderQuerySet(models.QuerySet):
    def get_cost(self):
        return self.prefetch_related('cooking_restaurant').\
            annotate(
            cost=Sum(F('items__quantity') * F('items__price'))
        )


class Order(models.Model):
    UNPROCESSED = 'UP'
    ASSEMBLY = 'AS'
    DELIVERY = 'DE'
    COMPLETED = 'CO'
    STATUS_CHOICES = [
        (UNPROCESSED, 'Необработанный'),
        (ASSEMBLY, 'Сборка'),
        (DELIVERY, 'Доставка'),
        (COMPLETED, 'Выполнен'),
    ]

    IN_CASH = 'CA'
    ELECTRONICALLY = 'EL'
    PAYMENT_METHOD_CHOICES = [
        (IN_CASH, 'Наличностью'),
        (ELECTRONICALLY, 'Электронно'),
    ]

    address = models.CharField(
        verbose_name='адрес',
        max_length=150,
    )

    firstname = models.CharField(
        verbose_name='имя',
        max_length=50,
    )

    lastname = models.CharField(
        verbose_name='фамилия',
        max_length=50,
    )

    phonenumber = PhoneNumberField(
        'мобильный номер',
        region='RU',
        db_index=True,
    )

    status = models.CharField(
        verbose_name='Статус',
        max_length=2,
        choices=STATUS_CHOICES,
        default=UNPROCESSED,
        db_index=True,
    )

    comment = models.TextField(
        verbose_name='комментарий',
        blank=True,
    )

    registered_at = models.DateTimeField(
        verbose_name='зарегистрирован в',
        auto_now_add=True,
        db_index=True,
    )

    called_at = models.DateTimeField(
        verbose_name='звонок в',
        blank=True,
        null=True,
        db_index=True,
    )

    delivered_at = models.DateTimeField(
        verbose_name='доставлен в',
        blank=True,
        null=True,
        db_index=True,
    )

    payment_method = models.CharField(
        verbose_name='Способ оплаты',
        max_length=2,
        choices=PAYMENT_METHOD_CHOICES,
        null=True,
        blank=True,
        db_index=True,
    )

    cooking_restaurant = models.ForeignKey(
        Restaurant,
        related_name='orders',
        verbose_name="ресторан",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f'Заказ № {self.id} {self.firstname} {self.lastname}\
            {self.address}'

    def get_possible_restaurants(
        self,
        menu: defaultdict,
        restaurants: dict,
        order_products: List
    ) -> List:
        if self.cooking_restaurant:
            return []

        possible_restaurants = []
        for restaurant, menu_products in menu.items():
            if not all(order_product in menu_products
                       for order_product in order_products):
                continue

            possible_restaurants.append(restaurants[restaurant].copy())

        return possible_restaurants

    @classmethod
    def get_model_description(cls):
        Description = namedtuple('Opts', ['app_label', 'model_name'])
        return Description(cls._meta.app_label, cls._meta.model_name)


class OrderItem(models.Model):
    order = models.ForeignKey(
        'Order',
        on_delete=models.CASCADE,
        verbose_name='заказ',
        related_name='items'
    )

    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        verbose_name='товар',
        related_name='order_items'
    )

    quantity = models.PositiveSmallIntegerField(
        verbose_name='количество',
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )

    price = models.DecimalField(
        verbose_name='цена',
        validators=[MinValueValidator(0), ],
        max_digits=8,
        decimal_places=2,
    )

    class Meta:
        verbose_name = 'элемент заказа'
        verbose_name_plural = 'элементы заказa'

    def __str__(self):
        return f'{self.product.name} {self.order.firstname}\
            {self.order.lastname} {self.order.address}'

    @classmethod
    def get_orders_products(cls, orders_ids: List) -> defaultdict:
        orders_items = cls.objects.filter(order__id__in=orders_ids)\
            .values('order', 'product')
        orders_products = defaultdict(list)
        for order_item in orders_items:
            orders_products[order_item['order']].append(order_item['product'])

        return orders_products
