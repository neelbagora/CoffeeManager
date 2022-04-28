from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Customer, Drink
from django.contrib import auth
import mysql.connector
import logging

# # Global connection to be used by all views for prepared statement queries
cnx = mysql.connector.connect(user='root', password="coffee",
                              host='127.0.0.1', port=1234,
                              database='coffeemanager')
global main_id



def preparedStatements(query):
    cursor = cnx.cursor()
    cursor.execute(query)
    return cursor


# Create your views here.

def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]


# --------------------------------------Admin/Staff Views-------------------------------------------------
def staffHome(request):
    return render(request, "coffeemanager/staffHome.html")


def addDrink(request):
    if request.method == "POST":
        try:
            Drink.objects.get(name=request.POST['name'])
            return render(request, 'coffeemanager/menu/addDrink.html', {'error': 'Drink already in the menu!'})
        except Drink.DoesNotExist:
            # ORM usage
            drink = Drink(name=request.POST['name'],
                          price=request.POST['price'])
            drink.save()
            return redirect('staffHome')  # Maybe redirect it to the menu url
    else:
        return render(request, 'coffeemanager/menu/addDrink.html')


def changeStatus(request):
    query = """
                    SELECT order_id, order_status 
                    from coffeemanager_orders order by order_id desc;
                    """
    cursor = preparedStatements(query)
    allStatus = dictfetchall(cursor)
    cursor.close()
    return render(request, "coffeemanager/changeStatus.html", context={'changeStatus': allStatus})

def changeStat(request):
    if request.method == 'POST':
        orderId = int(request.POST.get('order_id').replace("/",""))
        new_status = 0
        if 'Completed' in request.POST:
            new_status = 1
        elif 'In-Progress' in request.POST:
            new_status = 0
        elif 'Cancelled' in request.POST:
            new_status = 2
        query = f"""
                    UPDATE coffeemanager_orders
                    SET order_status = {new_status}
                    WHERE order_id = {orderId};
                       """
        preparedStatements(query)
        cnx.commit()
        return redirect('staffHome')

def allReviews(request):
    query = f'''SELECT review_id, coffeemanager_drink.name as drink, review, coffeemanager_customer.name as cust_name
           FROM coffeemanager_review 
           JOIN coffeemanager_drink ON drink_id = id JOIN coffeemanager_customer ON customer_id = email order by review_id desc;
        '''
    cursor = preparedStatements(query)
    allReviews = dictfetchall(cursor)
    cursor.close()
    return render(request, "coffeemanager/registration/allReviews.html", context={'allReviews': allReviews})



# -------------------------------------------Customer Views----------------------------------------------------
def home(request):
    return render(request, "coffeemanager/home.html")


def menu(request):
    if request.method == 'POST':
        # Search Results
        search_term = request.POST.get('search_term')
        query = f"""
                    SELECT id, name, price 
                    FROM coffeemanager_drink
                    WHERE name LIKE "%{search_term}%"
                    """
    else:
        # View Full Menu
        query = """
                SELECT id, name, price 
                from coffeemanager_drink;
                """
    cursor = preparedStatements(query)
    drinks = dictfetchall(cursor)
    cursor.close()
    return render(request, "coffeemanager/menu/menu.html", context={'drinks': updateMenu(request.user.username)})

def updateMenu(email):
    query = f'''
        SELECT id, name, price 
        FROM coffeemanager_drink 
        LEFT JOIN coffeemanager_cart ON drink_id = id
        WHERE customer_email = "{email}";
        '''
    cursor = preparedStatements(query)
    drinks = dictfetchall(cursor)
    cursor.close()

    query = """
            SELECT id, name, price 
            from coffeemanager_drink;
                """
    cursor = preparedStatements(query)
    all_drinks = dictfetchall(cursor)
    cursor.close()

    drink_ids = [x['id'] for x in drinks]
    new_drinks = []
    for drink in all_drinks:
        if drink['id'] in drink_ids:
            drink['added'] = True
        new_drinks.append(drink)
    return new_drinks

def addCartItem(request):
    email = request.user.username
    drink_id = request.POST.get('drink_id')
    
    transaction_start = "START TRANSACTION;"
    preparedStatements(transaction_start)

    insert = f''' 
            INSERT INTO coffeemanager_cart(customer_email,
                                            drink_id)
            VALUES("{email}", {drink_id});
            '''
    preparedStatements(insert)
    commit = "COMMIT;"
    preparedStatements(commit)
    cnx.commit()
    return render(request, "coffeemanager/menu/menu.html", context={'drinks': updateMenu(request.user.username)})

def removeCartItemMenu(request):
    email = request.user.username
    drink_id = request.POST.get('drink_id')

    transaction_start = "START TRANSACTION;"
    preparedStatements(transaction_start)

    insert = f''' 
            DELETE FROM coffeemanager_cart
            WHERE customer_email = "{email}" AND drink_id = {drink_id};
            '''
    preparedStatements(insert)
    commit = "COMMIT;"
    preparedStatements(commit)
    cnx.commit()

    return render(request, "coffeemanager/menu/menu.html", context={'drinks': updateMenu(request.user.username)})

def removeCartItem(request):
    email = request.user.username
    drink_id = request.POST.get('drink_id')

    transaction_start = "START TRANSACTION;"
    preparedStatements(transaction_start)

    insert = f''' 
            DELETE FROM coffeemanager_cart
            WHERE customer_email = "{email}" AND drink_id = {drink_id};
            '''
    preparedStatements(insert)
    commit = "COMMIT;"
    preparedStatements(commit)
    cnx.commit()

    query = f'''
        SELECT id, name, price 
        FROM coffeemanager_drink 
        INNER JOIN coffeemanager_cart ON drink_id = id
        WHERE customer_email = "{email}";
        '''
    cursor = preparedStatements(query)
    drinks = dictfetchall(cursor)
    cursor.close()

    return render(request, "coffeemanager/viewCart.html", context={'drinks': drinks})

def view_cart(request):
    email = request.user.username
    query = f'''
        SELECT id, name, price 
        FROM coffeemanager_drink 
        INNER JOIN coffeemanager_cart ON drink_id = id
        WHERE customer_email = "{email}";
        '''
    cursor = preparedStatements(query)
    drinks = dictfetchall(cursor)
    cursor.close()
    return render(request, "coffeemanager/viewCart.html", context={'drinks': drinks})

def submitOrder(request):
    maxId = """
            SELECT MAX(order_id) FROM coffeemanager_orders
            """
    order_id = preparedStatements(maxId).fetchone()[0]
    if not order_id:
        order_id = 0
    else:
        order_id += 1
    
    insert = f''' 
            INSERT INTO coffeemanager_orders(order_id,
                                            customer_id,
                                            drink_id,
                                            order_status,
                                            cart_order)
            VALUES({order_id}, "{request.user.username}", NULL, FALSE, TRUE);
            '''
    preparedStatements(insert)
    commit = "COMMIT;"
    preparedStatements(commit)
    cnx.commit()

    return render(request, "coffeemanager/confirmation.html", context={'confirmation': order_id})

def order(request):
    customer_id = request.user.username
    drink_id = request.POST.get('drink_id')

    # transaction_level = "SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;"
    # cursor.execute(transaction_level)
    # cursor.close()

    transaction_start = "START TRANSACTION;"
    preparedStatements(transaction_start)
    maxId = """
            SELECT MAX(order_id) FROM coffeemanager_orders
            """
    order_id = preparedStatements(maxId).fetchone()[0]
    if not order_id:
        order_id = 0
    else:
        order_id += 1

    insert = f''' 
            INSERT INTO coffeemanager_orders(order_id,
                                            customer_id,
                                            drink_id,
                                            order_status,
                                            cart_order)
            VALUES({order_id}, "{customer_id}", {drink_id}, FALSE, FALSE);
            '''
    preparedStatements(insert)
    commit = "COMMIT;"
    preparedStatements(commit)
    cnx.commit()

    return render(request, "coffeemanager/confirmation.html", context={'confirmation': order_id})

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
                # ORM Usage
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
            return render(request, 'coffeemanager/registration/login.html',
                          {'error': 'Username or password is incorrect!'})
    else:
        return render(request, 'coffeemanager/registration/login.html')


def logout(request):
    auth.logout(request)
    return redirect('home')

def status(request):
    customer_id = request.user.username
    query = f'''SELECT order_id, order_status from coffeemanager_orders where customer_id="{customer_id}";
    '''
    cursor = preparedStatements(query)
    status = dictfetchall(cursor)
    cursor.close()
    return render(request, "coffeemanager/menu/status.html", context={'status': status})

def addReview(request):
    email = request.user.username
    global main_id
    main_id = request.POST.get('drink_id')
    return render(request, "coffeemanager/menu/addReview.html")

def insertReview(request):
    email = request.user.username
    review = request.POST.get('reviewText')
    global main_id
    maxId = """
                SELECT MAX(review_id) FROM coffeemanager_review;
                """
    review_id = preparedStatements(maxId).fetchone()[0]
    if not review_id:
        review_id = 1
    else:
        review_id += 1
    query = f'''insert into coffeemanager_review VALUES ({review_id}, "{email}", {main_id} ,"{review}");
    '''
    preparedStatements(query)
    cnx.commit()
    return redirect('menu')

def myReviews(request):
    customer_id = request.user.username
    query = f'''SELECT review_id, name, review 
        FROM coffeemanager_review 
        JOIN coffeemanager_drink ON drink_id = id
        WHERE customer_id = "{customer_id}";
     '''
    cursor = preparedStatements(query)
    reviews = dictfetchall(cursor)
    cursor.close()
    return render(request, "coffeemanager/menu/myReviews.html", context={'reviews': reviews} )
