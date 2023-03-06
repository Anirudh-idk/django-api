from rest_framework import serializers
from . import models


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ["id", "email", "password"]
        extra_kwargs = {"password": {"write_only": True}}


class CustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = models.Customer
        fields = ["id", "user", "firstname", "lastname"]

    def create(
        self, validated_data
    ):  # first create user then use that to create custom user profile
        user_data = validated_data.pop("user")
        user1 = models.User.objects.create_user(**user_data)
        user1.is_customer = True
        user1.save()
        instance = models.Customer.objects.create(user=user1, **validated_data)
        return instance


class RestaurantSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = models.Restaurant
        fields = [
            "id",
            "user",
            "rest_name",
        ]

    def create(
        self, validated_data
    ):  # first create user then use that to create custom user profile
        user_data = validated_data.pop("user")
        user1 = models.User.objects.create_user(**user_data)
        user1.is_restaurant = True
        user1.save()
        instance = models.Restaurant.objects.create(user=user1, **validated_data)
        return instance


class DishSerializer(serializers.ModelSerializer):
    # restauraRestaurantS()
    class Meta:
        model = models.Dish
        fields = ["id", "name", "price", "restaurant"]


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Cart
        fields = ["id", "email"]


class CartitemSerializer(serializers.ModelSerializer):
    dish = serializers.ReadOnlyField(read_only=True)
    cart = serializers.ReadOnlyField(read_only=True)

    class Meta:
        model = models.Cartitem
        fields = [
            "id",
            "dish",
            "cart",
            "quantity",
        ]

    def save(self, data):  # custom save function to tackle with read_only field issue
        instance = models.Cartitem.objects.create(
            cart=data["cart"], dish=data["dish"], quantity=data["quantity"]
        )
        return instance


class OrderitemSerializer(serializers.ModelSerializer):
    dish = serializers.ReadOnlyField(read_only=True)
    quantity = serializers.ReadOnlyField(read_only=True)
    order = serializers.ReadOnlyField(read_only=True)

    class Meta:
        model = models.Orders
        fields = [
            "id",
            "dish",
            "quantity",
            "order",
        ]

    def save(self, data):  # custom save function to tackle with read_only field issue
        instance = models.Orderitem.objects.create(
            dish=data["dish"],
            order=data["order"],
            quantity=data["quantity"],
        )

        return instance


class OrderSerializer(serializers.ModelSerializer):
    customer = serializers.ReadOnlyField(read_only=True)
    restaurant = serializers.ReadOnlyField(read_only=True)

    class Meta:
        model = models.Orders
        fields = ["id", "customer", "restaurant", "created_at", "status"]

    def save(self, data):  # custom save function to tackle with read_only field issue
        instance = models.Orders.objects.create(
            customer=data["customer"],
            restaurant=data["restaurant"],
        )
        return instance
