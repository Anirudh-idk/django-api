from django.urls import path

from . import views

urlpatterns = [
    # User authentication and registration urls
    path("", views.LoginUserView.as_view()),
    path("register/customer/", views.CreateCustomerView.as_view()),
    path("register/restaurant/", views.CreateRestaurantView.as_view()),
    # customer related urls
    path("restaurants/", views.RestaurantListView.as_view()),
    path(
        "restaurants/<str:rest_name>/",
        views.Dish_RestaurantSpecificListView.as_view(),
    ),
    path(
        "create_dish/",
        views.DishCreateView.as_view(),
    ),
    path(
        "restaurants/<str:rest_name>/<int:pk>/",
        views.DishRetrieve_CartitemCreateView.as_view(),
    ),
    path(
        "restaurants/<str:rest_name>/<int:pk>/update/",
        views.DishUpdateDeleteView.as_view(),
    ),
    path(
        "restaurants/<str:rest_name>/<int:pk>/delete/",
        views.DishUpdateDeleteView.as_view(),
    ),
    path("placeorder/", views.PlaceOrderView.as_view()),
    # restaurant related urls
    path("orders/", views.RestaurantSpecificOrdersView.as_view()),
    path("orders/<int:pk>/", views.UpdateStatusView.as_view()),
]
