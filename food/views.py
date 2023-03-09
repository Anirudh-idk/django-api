from . import models, serializers
from proj1 import settings
from django.shortcuts import redirect
from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate, login
from rest_framework import generics, status, permissions


# Create your views here.

# user authentication view
class LoginUserView(generics.CreateAPIView):
    serializer_class = serializers.UserSerializer
    queryset = models.User.objects.all()

    def post(self, request, *args, **kwargs):
        try:
            user = authenticate(
                request,
                username=request.data["email"],
                password=request.data["password"],
            )
            if user is not None:
                login(request, user)
                if request.user.is_customer == True:
                    return redirect("restaurants/")
                else:
                    return redirect("orders/")
            else:
                return Response(
                    data={"message": "wrong credentials"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
        except Exception as err:
            return Response(
                {str(type(err)): str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# Type of User specific Registration views
class CreateCustomerView(generics.CreateAPIView):
    serializer_class = serializers.CustomerSerializer
    queryset = models.User.objects.filter(is_customer=True).values()

    def get(self, request, *args, **kwargs):
        return Response(data={})

    def post(self, request, *args, **kwargs):
        try:
            cust = serializers.CustomerSerializer(data=request.data)
            if cust.is_valid(raise_exception=True):
                cart = serializers.CartSerializer(
                    data={"email": request.data.get("user.email")}
                )  # creates cart at the time of registration
                if cart.is_valid(raise_exception=True):
                    cart.save()
                    cust.save()
                    return Response(cust.data)
        except Exception as err:
            return Response(
                {str(type(err)): str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CreateRestaurantView(generics.ListCreateAPIView):
    serializer_class = serializers.RestaurantSerializer
    queryset = models.User.objects.filter(is_restaurant=True).values()

    def get(self, request, *args, **kwargs):
        return Response(data={})

    def post(self, request, *args, **kwargs):
        try:
            rest = serializers.RestaurantSerializer(data=request.data)
            if rest.is_valid(raise_exception=True):
                rest.save()
                return Response(rest.data)
        except Exception as err:
            return Response(
                {str(type(err)): str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# Customer Useful Views
class RestaurantListView(generics.ListAPIView):
    queryset = models.Restaurant.objects.distinct()
    serializer_class = serializers.RestaurantSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, *args, **kwargs):
        qs = list(models.Restaurant.objects.distinct().values_list("rest_name"))
        out_dict = {}
        try:
            if qs:
                for i in range(len(qs)):
                    out_dict[f"Restaurant{i+1}"] = qs[i][0]
                return Response(out_dict)
            else:
                return Response({"message": "No Restaurants available currently"})
        except Exception as err:
            return Response(
                {str(type(err)): str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DishCreateView(generics.CreateAPIView):
    queryset = models.Dish.objects.all()
    serializer_class = serializers.DishSerializer
    permission_classes = [permissions.IsAuthenticated]


class Dish_RestaurantSpecificListView(generics.ListAPIView):
    queryset = models.Dish.objects.all()
    serializer_class = serializers.DishSerializer
    permission_classes = [permissions.IsAuthenticated]

    lookup_field = "rest_name"

    def get(self, request, rest_name, *args, **kwargs):
        try:
            restaurant = models.Restaurant.objects.get(rest_name=rest_name)
        except:
            restaurant = None
        if restaurant:
            qs = models.Dish.objects.filter(restaurant=restaurant.pk)
            if qs:
                serializer = serializers.DishSerializer(qs, many=True)
                return Response(serializer.data)
            else:
                return Response({"message": "No Dishes available"})
        else:
            return Response({"message": "Please give valid restaurant name"})


class DishUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Dish.objects.all()
    serializer_class = serializers.DishSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, pk, rest_name, *args, **kwargs):
        try:
            qs = models.Dish.objects.get(
                pk=pk, restaurant=models.Restaurant.objects.get(rest_name=rest_name).pk
            )
            serializer = serializers.DishSerializer(qs, data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data)
        except Exception as err:
            return Response(
                {str(type(err)): str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, pk, rest_name, *args, **kwargs):
        try:
            qs = models.Dish.objects.get(
                pk=pk, restaurant=models.Restaurant.objects.get(rest_name=rest_name).pk
            )
            if qs:
                qs.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    {"message": "Dish with the given Dish_id doesn't exist"}
                )
        except Exception as err:
            return Response(
                {str(type(err)): str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DishRetrieve_CartitemCreateView(generics.ListCreateAPIView):
    queryset = models.Dish.objects.all()
    serializer_class = serializers.CartitemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk, rest_name, *args, **kwargs):
        try:
            queryset = models.Dish.objects.get(
                pk=pk, restaurant=models.Restaurant.objects.get(rest_name=rest_name).pk
            )
            return Response(serializers.DishSerializer(queryset).data)
        except Exception as err:
            return Response(
                {str(type(err)): str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request, pk, *args, **kwargs):
        try:
            cartitem = serializers.CartitemSerializer(
                data={
                    "cart": request.user,
                    "dish": models.Dish.objects.get(pk=pk),
                    "quantity": request.data.get("quantity"),
                }
            )
            if cartitem.is_valid(raise_exception=True):
                output = cartitem.save(
                    data={
                        "cart": models.Cart.objects.get(email=request.user.email),
                        "dish": models.Dish.objects.get(pk=pk),
                        "quantity": request.data.get("quantity"),
                    }
                )
                return Response(
                    {
                        "cart": output.cart.email,
                        "dish": output.dish.name,
                        "quanity": output.quantity,
                    }
                )
        except Exception as err:
            return Response(
                {str(type(err)): str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PlaceOrderView(generics.ListAPIView):
    queryset = models.Orders.objects.all()
    serializer_class = serializers.OrderitemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            out_dict = {}  # dictionary to output - no use just to show some output
            for restauarnt in models.Restaurant.objects.distinct():

                qs_cartitem = models.Cartitem.objects.filter(
                    cart=models.Cart.objects.get(email=request.user.email),
                    dish__restaurant=restauarnt.id,
                )

                if qs_cartitem:
                    data_order = {
                        "customer": request.user,
                        "restaurant": restauarnt,
                    }
                    order = serializers.OrderSerializer(
                        data=data_order
                    )  # making a new order entry for all the items in the given cart

                    if order.is_valid(raise_exception=True):
                        order = order.save(data=data_order)

                    orderitem_dict = {}
                    for i in range(len(list(qs_cartitem))):
                        item = list(qs_cartitem)[i]
                        data = {
                            "dish": item.dish,
                            "quantity": item.quantity,
                            "order": order,
                        }

                        Orderitem = serializers.OrderitemSerializer(data=data)

                        if Orderitem.is_valid(raise_exception=True):
                            output = Orderitem.save(data=data)
                            orderitem_dict[f"Item{i+1}"] = {
                                "dish": output.dish.name,
                                "quantity": output.quantity,
                            }

                    qs_cartitem.delete()
                    out_dict[restauarnt.rest_name] = orderitem_dict

                else:
                    return Response(data={"message": "empty cart"})
            return Response(out_dict)

        except Exception as err:
            return Response(
                {str(type(err)): str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# Restaurant Useful Views
class RestaurantSpecificOrdersView(generics.ListAPIView):
    queryset = models.Orders.objects.all()
    serializer_class = serializers.OrderitemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        out_dict1 = {}
        out_dict2 = {}
        try:
            restname = models.Restaurant.objects.get(user=request.user)
            qs = models.Orders.objects.filter(restaurant=restname)
            if qs:
                for order in qs:
                    qs_orderitems = models.Orderitem.objects.filter(order=order)

                    orderitem_dict = {}

                    for i in range(len(list(qs_orderitems))):
                        item = list(qs_orderitems)[i]
                        orderitem_dict[f"Item{i+1}"] = {
                            "dish": item.dish.name,
                            "quantity": item.quantity,
                        }

                    out_dict2["Order_id"] = order.pk
                    out_dict2["customer"] = order.customer.email
                    out_dict2["status"] = order.status
                    out_dict2["Order"] = orderitem_dict

                    out_dict1[order.pk] = out_dict2
                return Response(out_dict1)
            else:
                return Response({"message": "No orders"})
        except Exception as err:
            return Response(
                {str(type(err)): str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UpdateStatusView(generics.RetrieveUpdateAPIView):
    queryset = models.Orders.objects.all()
    serializer_class = serializers.OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        order = models.Orders.objects.get(pk=pk)
        qs_orderitems = models.Orderitem.objects.filter(order=order)
        if qs_orderitems:
            out_dict = {}
            orderitem_dict = {}

            for i in range(len(list(qs_orderitems))):
                item = list(qs_orderitems)[i]
                orderitem_dict[f"Item{i+1}"] = {
                    "dish": item.dish.name,
                    "quantity": item.quantity,
                }

            out_dict["customer"] = order.customer.email
            out_dict["status"] = order.status
            out_dict["Order"] = orderitem_dict

            return Response(out_dict)
        else:
            return Response({"message": "Empty Order"})

    def update(self, request, pk, *args, **kwarg):
        try:
            order = models.Orders.objects.get(pk=pk)
            order.status = request.data.get("status")
            order.save(update_fields=["status"])
            send_mail(
                "Order status updated",
                f"Your Order is {order.status}",
                settings.EMAIL_HOST_USER,
                [f"{order.customer.email}"],
                fail_silently=False,
            )
            return Response(
                {
                    "m+essage": f'Order status is  updated to {request.data.get("status")}'
                }
            )

        except Exception as err:
            return Response(
                {str(type(err)): str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
