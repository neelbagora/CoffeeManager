from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('signup', views.signup, name="signup"),
    path('login', views.login, name="login"),
    path('logout', views.logout, name="logout"),
    path('staffHome', views.staffHome, name="staffHome"),
    path('addDrink', views.addDrink, name="addDrink"),
    path('orders', views.orders, name="orders")
]
