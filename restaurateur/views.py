import sys

from django import forms
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Case, Value, When
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from geopy.distance import distance

from foodcartapp.models import (Order, OrderItem, Product, Restaurant,
                                RestaurantMenuItem)
from geo.models import Location


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    products_with_restaurant_availability = []
    for product in products:
        availability = {
            item.restaurant_id: item.availability
            for item in product.menu_items.all()
        }
        ordered_availability = [availability.get(
            restaurant.id, False) for restaurant in restaurants]

        products_with_restaurant_availability.append(
            (product, ordered_availability)
        )

    return render(
        request, template_name="products_list.html", context={
            'products_with_restaurant_availability':
            products_with_restaurant_availability,
            'restaurants': restaurants,
        }
    )


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    orders = Order.objects.get_cost().exclude(status=Order.COMPLETED)\
        .order_by(
            Case(
                When(status=Order.UNPROCESSED, then=Value(0)),
                When(status=Order.ASSEMBLY, then=Value(1)),
                default=Value(2),
            ),
            '-id',
    )
    orders_ids = [order.id for order in orders]
    orders_products = OrderItem.get_orders_products(orders_ids)

    products_ids = [
        order_item['product'] for order_item in OrderItem.objects
        .filter(order__id__in=orders_ids).distinct().values('product')
    ]

    menu_items = RestaurantMenuItem.objects.get_available_menu_items(
        products_ids
    )

    menus, restaurants = RestaurantMenuItem.get_restaurants_menus(menu_items)

    order_cards = []
    for order in orders:
        possible_restaurants = order.get_possible_restaurants(
            menus,
            restaurants,
            orders_products[order.id]
        )
        order_cards.append(
            {'order': order, 'possible_restaurants': possible_restaurants, }
        )

    addresses = set()
    for order_card in order_cards:
        if order_card['order'].cooking_restaurant:
            continue
        if not order_card['possible_restaurants']:
            continue

        addresses.add(order_card['order'].address)
        for restaurant in order_card['possible_restaurants']:
            addresses.add(restaurant['address'])

    locations_catalog = {}
    locations = Location.objects.filter(address__in=addresses).values(
        'address',
        'latitude',
        'longitude',
    )
    for location in locations:
        locations_catalog[location['address']] = {
            'latitude': location['latitude'],
            'longitude': location['longitude'],
        }

    for order_card in order_cards:
        if order_card['order'].cooking_restaurant:
            continue
        if not order_card['possible_restaurants']:
            continue

        order_location = locations_catalog.get(
            order_card['order'].address, None
        )
        for restaurant in order_card['possible_restaurants']:
            restaurant['distance'] = sys.maxsize
            restaurant['distance_error'] = True
            if not order_location:
                continue

            restaurant_location = locations_catalog.get(
                restaurant['address'], None
            )
            if not restaurant_location:
                continue

            distance_km = distance(
                (order_location['latitude'], order_location['longitude']),
                (restaurant_location['latitude'],
                 restaurant_location['longitude'])
            ).km

            restaurant['distance'] = distance_km
            restaurant['distance_error'] = False

        if all(
            restaurant['distance_error']
            for restaurant in order_card['possible_restaurants']
        ):
            continue

        order_card['possible_restaurants'].sort(
            key=Location.get_distance_from_restaurant
        )

    return render(
        request, template_name='order_items.html', context={
            'order_cards': order_cards,
            'order_model_description': Order.get_model_description()
        }
    )
