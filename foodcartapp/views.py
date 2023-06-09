import logging

import requests
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer

from geo.models import Location

from .models import Order, OrderItem, Product

logger = logging.getLogger(__file__)


class OrderItemSerializer(ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', ]


class OrderSerializer(ModelSerializer):
    products = OrderItemSerializer(
        many=True,
        allow_empty=False,
        write_only=True
    )

    class Meta:
        model = Order
        fields = [
            'id',
            'address',
            'firstname',
            'lastname',
            'phonenumber',
            'products'
        ]


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your doorstep',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
def register_order(request):
    serializer = OrderSerializer(data=request.data)
    try:
        serializer.is_valid(raise_exception=True)
    except (ValidationError) as error:
        return Response(
            {'error': error},
            status=status.HTTP_406_NOT_ACCEPTABLE
        )
    with transaction.atomic():
        order = Order.objects.create(
            address=serializer.validated_data['address'],
            firstname=serializer.validated_data['firstname'],
            lastname=serializer.validated_data['lastname'],
            phonenumber=serializer.validated_data['phonenumber'],
        )

        products_fields = serializer.validated_data['products']
        order_items = [
            OrderItem(
                order=order,
                price=fields['product'].price,
                **fields
            ) for fields in products_fields
        ]
        OrderItem.objects.bulk_create(order_items)

    try:
        Location.save_location(order.address)
    except requests.ConnectionError:
        logger.warning(
            'Connection error. Location for order %s'
            ' was not saved',
            order
        )

    serializer = OrderSerializer(order)
    return Response(serializer.data)
