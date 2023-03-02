from django.urls import path

from . import views

urlpatterns = [
    path('products/',views.DishListCreateview.as_view()),
    path('products/<int:pk>/update/', views.DishUpdateDelete.as_view()),
    path('products/<int:pk>/delete/', views.DishUpdateDelete.as_view()),
    path('products/<int:pk>/', views.cartitemcreate.as_view()),
    path('products/<int:pk>/', views.dishretrieve.as_view()),
    path('register/customer/',views.createcustomer.as_view()),
    path('register/restaurant/',views.createrestaurant.as_view()),
    path('',views.loginuser.as_view()),
]