from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect

# Create your views here.

# user authentication view
class loginuser(generics.CreateAPIView):
    serializer_class = userserializer
    queryset = user.objects.all()

    def post(self, request, *args, **kwargs):
        user = authenticate(
            request, username=request.data["email"], password=request.data["password"]
        )
        if user is not None:
            print("what")
            login(request, user)
            return redirect("products/")
        else:
            print("smtg")
            return Response(
                data={"message": "wrong credens"}, status=status.HTTP_401_UNAUTHORIZED
            )


# Type of User specific Registration views
class createcustomer(generics.CreateAPIView):
    serializer_class = cust_serializer
    queryset = user.objects.filter(is_customer=True).values()

    def get(self, request, *args, **kwargs):
        return Response(data={})

    def post(self, request, *args, **kwargs):
        cust = cust_serializer(data=request.data)
        if cust.is_valid(raise_exception=True):
            cart = Cart_serializer(
                data={"email": request.data.get("user.email")}
            )  # creates cart at the time of registration
            if cart.is_valid(raise_exception=True):
                cart.save()
                cust.save()
            return Response(cust.data)


class createrestaurant(generics.ListCreateAPIView):
    serializer_class = rest_serializer
    queryset = user.objects.filter(is_restaurant=True).values()

    def get(self, request, *args, **kwargs):
        return Response(data={})

    def post(self, request, *args, **kwargs):
        rest = rest_serializer(data=request.data)
        if rest.is_valid(raise_exception=True):
            rest.save()
            return Response(rest.data)


# Dishes CRUD views(made while learning, might remove update and delete ones later)
class DishListCreateview(generics.ListCreateAPIView):
    queryset = Dishes.objects.all()
    serializer_class = Dish_serializer
    permission_classes = [permissions.IsAuthenticated]


class DishUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    queryset = Dishes.objects.all()
    serializer_class = Dish_serializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, pk, *args, **kwargs):
        queryset = Dishes.objects.get(pk=pk)
        serializer = Dish_serializer(queryset, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)

    def delete(self, request, pk, *args, **kwargs):
        queryset = Dishes.objects.get(pk=pk)
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class dishretrieve(generics.RetrieveAPIView):
    queryset = Dishes.objects.all()
    serializer_class = Dish_serializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        queryset = Dishes.objects.get(pk=pk)
        print(pk)
        return Response(Dish_serializer(queryset).data)


# Cart item creation view
class cartitemcreate(generics.CreateAPIView):
    queryset = Cartitem.objects.all()
    serializer_class = Cartitem_serializer

    def create(self, request, pk, *args, **kwargs):
        cartitem = Cartitem_serializer(
            data={
                "cart": request.user,
                "dish": Dishes.objects.get(pk=pk),
                "quantity": request.data.get("quantity"),
            }
        )
        if cartitem.is_valid(raise_exception=True):
            output = cartitem.save(
                data={
                    "cart": Cart.objects.get(email=request.user.email),
                    "dish": Dishes.objects.get(pk=pk),
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


class make_order(generics.ListAPIView):
    queryset = models.Orders.objects.all()
    serializer_class = Orderitem_serializer

    def get(self, request, *args, **kwargs):
        qs = models.Cartitem.objects.filter(
            cart=Cart.objects.get(email=request.user.email)
        )
        if qs:
            order = Order_serializer(
                data={"customer": request.user}
            )  # making a new order entry for all the items in the given cart

            if order.is_valid(raise_exception=True):
                ordersmtg = order.save(data={"customer": request.user})
            out_dict = {}  # dictionary to output - no use just to give some output

            for item in list(qs):
                data = {
                    "dish": item.dish,
                    "quantity": item.quantity,
                    "order": ordersmtg,
                    "restaurant_name": item.dish.restaurant,
                }

                Orderitem = Orderitem_serializer(data=data)

                if Orderitem.is_valid(raise_exception=True):
                    output = Orderitem.save(data=data)
                    out_dict[item.pk] = {
                        "dish": output.dish.name,
                        "quantity": output.quantity,
                        "order": ordersmtg.id,
                        "restaurant_name": output.restaurant_name.rest_name,
                    }

            qs.delete()
            return Response(
                {ordersmtg.customer.email: out_dict, "status": ordersmtg.status}
            )

        else:
            return Response(data={"message": "empty cart"})


"""
class RestaurantSpecificOrders(generics.ListAPIView):
    queryset = models.Orders.objects.all()
    serializer_class = Orderitem_serializer
    def get(self,request,*args,**kwargs):
        rest_name = list(models.restaurant.objects.filter(user = request.user))[0]
        qs = models.Orders.objects.filter(restaurant_name = rest_name).values()
        return Response(Orderitem_serializer(qs,many = True).data)
        """
