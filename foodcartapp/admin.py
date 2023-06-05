import logging

import requests
from django.contrib import admin
from django.shortcuts import redirect, reverse
from django.templatetags.static import static
from django.utils.html import format_html
from django.utils.http import url_has_allowed_host_and_scheme

from geo.models import Location

from .models import (Order, OrderItem, Product, ProductCategory, Restaurant,
                     RestaurantMenuItem)

logger = logging.getLogger(__file__)


class RestaurantMenuItemInline(admin.TabularInline):
    model = RestaurantMenuItem
    extra = 0


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    search_fields = [
        'name',
        'address',
        'contact_phone',
    ]
    list_display = [
        'name',
        'address',
        'contact_phone',
    ]
    inlines = [
        RestaurantMenuItemInline
    ]

    def response_change(self, request, obj):
        try:
            Location.save_location(obj.address)
        except requests.ConnectionError:
            logger.warning(
                'Connection error. Location for restaurant %s'
                ' was not saved',
                obj
            )
        return super().response_change(request, obj)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'get_image_list_preview',
        'name',
        'category',
        'price',
    ]
    list_display_links = [
        'name',
    ]
    list_filter = [
        'category',
    ]
    search_fields = [
        # FIXME SQLite can not convert letter case for cyrillic words properly,
        # so search will be buggy.
        # Migration to PostgreSQL is necessary
        'name',
        'category__name',
    ]

    inlines = [
        RestaurantMenuItemInline
    ]
    fieldsets = (
        ('Общее', {
            'fields': [
                'name',
                'category',
                'image',
                'get_image_preview',
                'price',
            ]
        }),
        ('Подробно', {
            'fields': [
                'special_status',
                'description',
            ],
            'classes': [
                'wide'
            ],
        }),
    )

    readonly_fields = [
        'get_image_preview',
    ]

    class Media:
        css = {
            "all": (
                static("admin/foodcartapp.css")
            )
        }

    def get_image_preview(self, obj):
        if not obj.image:
            return 'выберите картинку'
        return format_html(
            '<img src="{url}" style="max-height: 200px;"/>',
            url=obj.image.url
        )
    get_image_preview.short_description = 'превью'

    def get_image_list_preview(self, obj):
        if not obj.image or not obj.id:
            return 'нет картинки'
        edit_url = reverse('admin:foodcartapp_product_change', args=(obj.id,))
        return format_html(
            '<a href="{edit_url}"><img src="{src}" style="max-height: 50px;"/>\
                </a>',
            edit_url=edit_url, src=obj.image.url
        )
    get_image_list_preview.short_description = 'превью'


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    pass


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = (OrderItemInline,)
    list_display = (
        '__str__',
        'phonenumber',
        'status',
        'payment_method',
        'comment',
        'registered_at'
    )
    readonly_fields = ('registered_at',)

    def response_change(self, request, obj):
        try:
            Location.save_location(obj.address)
        except requests.ConnectionError:
            logger.warning(
                'Connection error. Location for order %s'
                ' was not saved',
                obj
            )

        if '_save' not in request.POST:
            return super().response_change(request, obj)

        next_url = request.GET.get('next', None)
        if url_has_allowed_host_and_scheme(next_url, None):
            return redirect(next_url)

        return super().response_change(request, obj)

    def save_model(self, request, obj, form, change):
        if obj.cooking_restaurant and obj.status == obj.UNPROCESSED:
            obj.status = obj.ASSEMBLY
        super().save_model(request, obj, form, change)
