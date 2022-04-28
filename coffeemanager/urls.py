from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name="home"),
    path('signup', views.signup, name="signup"),
    path('login', views.login, name="login"),
    path('logout', views.logout, name="logout"),
    path('staffHome', views.staffHome, name="staffHome"),
    path('addDrink', views.addDrink, name="addDrink"),
    path('menu', views.menu, name="menu"),
    path('order', views.order, name="order"),
    path('status', views.status, name="status"),
    path('changeStatus', views.changeStatus, name="changeStatus"),
    path('viewCart', views.view_cart, name="viewCart"),
    path('addCartItem', views.addCartItem, name="addCartItem"),
    path('removeCartItemMenu', views.removeCartItemMenu, name="removeCartItemMenu"),
    path('removeCartItem', views.removeCartItem, name="removeCartItem"),
    path('submitOrder', views.submitOrder, name="submitOrder"),
    path('changeStat', views.changeStat, name="changeStat"),
    path('addReview', views.addReview, name="addReview"),
    path('insertReview', views.insertReview, name="insertReview"),
    path('myReviews', views.myReviews, name="myReviews")
]
