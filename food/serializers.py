from rest_framework import serializers
from . import models


class userserializer(serializers.ModelSerializer):
    class Meta:
        model = models.user
        fields = ["id", "email", "password"]
        extra_kwargs = {"password": {"write_only": True}}


class cust_serializer(serializers.ModelSerializer):
    user = userserializer()

    class Meta:
        model = models.customer
        fields = ["id", "user", "firstname", "lastname"]

    def create(
        self, validated_data
    ):  # first create user then use that to create user profile
        user_data = validated_data.pop("user")
        user1 = models.user.objects.create_user(**user_data)
        user1.is_customer = True
        user1.save()
        instance = models.customer.objects.create(user=user1, **validated_data)
        return instance


class rest_serializer(serializers.ModelSerializer):
    user = userserializer()

    class Meta:
        model = models.restaurant
        fields = [
            "id",
            "user",
            "rest_name",
        ]

    def create(
        self, validated_data
    ):  # first create user then use that to create user profile
        user_data = validated_data.pop("user")
        user1 = models.user.objects.create_user(**user_data)
        user1.is_restaurant = True
        user1.save()
        instance = models.restaurant.objects.create(user=user1, **validated_data)
        return instance


class Dish_serializer(serializers.ModelSerializer):
    # restaurant = rest_serializer()
    class Meta:
        model = models.Dishes
        fields = ["id", "name", "price", "restaurant"]


class Cart_serializer(serializers.ModelSerializer):
    class Meta:
        model = models.Cart
        fields = ["id", "email"]


class Cartitem_serializer(serializers.ModelSerializer):
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


class Orderitem_serializer(serializers.ModelSerializer):
    dish = serializers.ReadOnlyField(read_only=True)
    quantity = serializers.ReadOnlyField(read_only=True)
    order = serializers.ReadOnlyField(read_only=True)
    restaurant_name = serializers.ReadOnlyField(read_only=True)

    class Meta:
        model = models.Orders
        fields = [
            "id",
            "dish",
            "quantity",
            "order",
            "restaurant_name",
        ]

    def save(self, data):  # custom save function to tackle with read_only field issu
        instance = models.Orderitem.objects.create(
            dish=data["dish"],
            order=data["order"],
            quantity=data["quantity"],
            restaurant_name=data["restaurant_name"],
        )

        return instance


class Order_serializer(serializers.ModelSerializer):
    customer = serializers.ReadOnlyField(read_only=True)

    class Meta:
        model = models.Orders
        fields = ["id", "customer", "status"]

    def save(self, data):  # custom save function to tackle with read_only field issue
        instance = models.Orders.objects.create(customer=data["customer"])
        return instance
