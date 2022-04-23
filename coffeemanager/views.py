from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Customer, Drink
from django.contrib import auth
import mysql.connector
# Create your views here.


def home(request):
    return render(request, "coffeemanager/home.html")


def staffHome(request):
    return render(request, "coffeemanager/staffHome.html")

def orders(request):
    cnx = mysql.connector.connect(user='root', password="coffee",
                                  host='127.0.0.1:1234',
                                  database='coffeemanager')
    return render(request, "coffeemanager/home.html")


def addDrink(request):
    if request.method == "POST":
        try:
            Drink.objects.get(name=request.POST['name'])
            return render(request, 'coffeemanager/menu/addDrink.html', {'error': 'Drink already in the menu!'})
        except Drink.DoesNotExist:
            drink = Drink(name=request.POST['name'],
                          price=request.POST['price'])
            drink.save()
            return redirect('staffHome')  # Maybe redirect it to the menu url
    else:
        return render(request, 'coffeemanager/menu/addDrink.html')


def signup(request):
    if request.method == "POST":
        if request.POST['password1'] == request.POST['password2']:
            try:
                User.objects.get(username=request.POST['username'])
                return render(request, 'coffeemanager/registration/signup.html', {'error': 'Email already registered!'})
            except User.DoesNotExist:
                user = User.objects.create_user(
                    request.POST['username'], password=request.POST['password1'], first_name=request.POST['name'])
                auth.login(request, user)
                customer = Customer(
                    name=request.POST['name'], email=request.POST['username'])
                customer.save()
                return redirect('home')
        else:
            return render(request, 'coffeemanager/registration/signup.html', {'error': 'Password does not match!'})
    else:
        return render(request, 'coffeemanager/registration/signup.html')


def login(request):
    if request.method == 'POST':
        user = auth.authenticate(
            username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            auth.login(request, user)
            if user.is_staff:
                return redirect('staffHome')
            return redirect('home')
        else:
            return render(request, 'coffeemanager/registration/login.html', {'error': 'Username or password is incorrect!'})
    else:
        return render(request, 'coffeemanager/registration/login.html')


def logout(request):
    auth.logout(request)
    return redirect('home')
