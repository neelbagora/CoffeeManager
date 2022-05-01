from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import *
from django.contrib import auth
import mysql.connector
import logging
from django.contrib.auth.decorators import login_required

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

def changeOrderStatus(request):
    query = """
        SELECT id, order_status 
        from coffeemanager_orders order by id desc;
        """
    cursor = preparedStatements(query)
    allStatus = dictfetchall(cursor)
    cursor.close()
    return render(request, "coffeemanager/changeStatus.html", context={'changeStatus': allStatus})

def changeStoreStatus(request):
    transaction_start = "START TRANSACTION;"
    preparedStatements(transaction_start)

    store = "CoffeeShop"
    query = f'''
            SELECT open FROM coffeemanager_shop
            WHERE name = "{store}";
        '''
    is_open = preparedStatements(query).fetchone()[0] == 1

    query = f'''
            UPDATE coffeemanager_shop 
            SET open = {not is_open}
            WHERE name = "{store}";
        '''
    preparedStatements(query)
    return render(request, "coffeemanager/staffHome.html", context={'status': not is_open, "store": store})

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
                    WHERE id = {orderId};
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
  
  
def prevOrders(request):
  query = f'''SELECT id, order_id, customer_id 
          FROM coffeemanager_orders 
          WHERE order_status = True
          ORDER BY order_id desc;
       '''
  
  cursor = preparedStatements(query)
  prevOrders = dictfetchall(cursor)
  cursor.close()
  return render(request, "coffemanager/menu/previousOrders.html", context={'prevOrders': prevOrders})
          

# -------------------------------------------Customer Views----------------------------------------------------
def home(request):
    store = "CoffeeShop"
    query = f'''
        SELECT open FROM coffeemanager_shop WHERE name = "{store}";
        '''
    is_open = preparedStatements(query).fetchone()[0] == 1
    return render(request, "coffeemanager/home.html", {"status": is_open, "store" : store})

def menu(request):
    search_term = None
    if request.method == 'POST':
        # Search Results
        search_term = request.POST.get('search_term')
    return render(request, "coffeemanager/menu/menu.html", context={'drinks': updateMenu(request.user.username, search_term)})

def updateMenu(email, search_term = None):
    query = """
            SELECT drink.id, name, price, quantity 
            from coffeemanager_drink AS drink
            LEFT JOIN coffeemanager_cart_item ON drink.id = product_id
            """
    if search_term:
        query = query + f''' WHERE name LIKE "%{search_term}%";'''
    cursor = preparedStatements(query)
    all_drinks = dictfetchall(cursor)
    cursor.close()
    return all_drinks

def addCartItem(request):
    email = request.user.username
    drink_id = request.POST.get('drink_id')
    
    transaction_start = "START TRANSACTION;"
    preparedStatements(transaction_start)

    # Get cart_id associated with email.
    query = f'''
        SELECT id FROM coffeemanager_cart WHERE customer_email = "{request.user.username}";
        '''
    cart_id = preparedStatements(query).fetchone()
    
    # If no cart_id, create a new cart
    if not cart_id:
        # ORM Usage
        cart = Cart(customer_email = email)
        cart.save()
        commit = "COMMIT;"
        preparedStatements(commit)

        # Get cart_id
        query = f'''
            SELECT id FROM coffeemanager_cart WHERE customer_email = "{request.user.username}";
            '''
        cart_id = preparedStatements(query).fetchone()[0]
    else:
        # Cart_id found, get result
        cart_id = cart_id[0]

    # Get all the items from the cart matching the cart_id and product_id
    query = f'''
        SELECT id, cart_id, product_id, quantity FROM coffeemanager_cart_item
        WHERE cart_id = {cart_id} AND product_id = {drink_id};
        '''
    cursor = preparedStatements(query).fetchone()
    
    # Check if null result is returned.
    if not cursor:
        transaction_start = "START TRANSACTION;"
        preparedStatements(transaction_start)
        # ORM Usage
        cart_item = Cart_Item(product_id = drink_id, cart_id = cart_id, quantity = 1)
        cart_item.save()
        commit = "COMMIT;"
        preparedStatements(commit)
    else:
        # If not null, increment the quantity of existing cart_item
        update = f''' 
                UPDATE coffeemanager_cart_item
                SET quantity = {cursor[3] + 1}
                WHERE cart_id = {cart_id} AND product_id = {drink_id};
                '''
        preparedStatements(update)
        commit = "COMMIT;"
        preparedStatements(commit)
        cnx.commit()
    
    return render(request, "coffeemanager/menu/menu.html", context={'drinks': updateMenu(request.user.username)})

def removeCartItemMenu(request):
    email = request.user.username
    drink_id = request.POST.get('drink_id')

    transaction_start = "START TRANSACTION;"
    preparedStatements(transaction_start)

    # Get cart id matching the email
    query = f'''
        SELECT id FROM coffeemanager_cart WHERE customer_email = "{request.user.username}";
        '''
    cart_id = preparedStatements(query).fetchone()[0]

    # Find the quantity of the product in cart_item that is associated with cart_id
    query = f'''
        SELECT quantity FROM coffeemanager_cart_item WHERE cart_id = {cart_id} AND product_id = {drink_id};
        '''
    quantity = preparedStatements(query).fetchone()[0]

    if quantity > 1:
        # Decrement if > 1
        update = f''' 
                UPDATE coffeemanager_cart_item
                SET quantity = {quantity - 1}
                WHERE cart_id = {cart_id} AND product_id = {drink_id};
                '''
        preparedStatements(update)
        commit = "COMMIT;"
        preparedStatements(commit)
        cnx.commit()
    else:
        # Delete if = 1
        delete = f''' 
                DELETE FROM coffeemanager_cart_item
                WHERE cart_id = {cart_id} AND product_id = {drink_id};
                '''
        preparedStatements(delete)
        commit = "COMMIT;"
        preparedStatements(commit)
        cnx.commit()

    return render(request, "coffeemanager/menu/menu.html", context={'drinks': updateMenu(request.user.username)})

def removeCartItem(request):
    email = request.user.username
    drink_id = request.POST.get('drink_id')

    transaction_start = "START TRANSACTION;"
    preparedStatements(transaction_start)
    
    # Get and delete all the cart_items matching the cart id
    query = f'''
        SELECT id FROM coffeemanager_cart WHERE customer_email = "{request.user.username}";
        '''
    cart_id = preparedStatements(query).fetchone()[0]

    query = f'''
        SELECT quantity FROM coffeemanager_cart_item
        WHERE cart_id = {cart_id} AND product_id = {drink_id}; 
        '''
    quantity = preparedStatements(query).fetchone()[0]

    if quantity > 1:
        query = f''' 
                UPDATE coffeemanager_cart_item
                SET quantity = {quantity - 1}
                WHERE cart_id = {cart_id} AND product_id = {drink_id};
                '''
    else:
        query = f''' 
                DELETE FROM coffeemanager_cart_item
                WHERE cart_id = {cart_id} AND product_id = {drink_id};
                '''
    preparedStatements(query)
    commit = "COMMIT;"
    preparedStatements(commit)
    cnx.commit()

    # Get all the cart items in the cart
    query = f'''
        SELECT tab1.id, name, price, quantity FROM coffeemanager_drink AS tab1
        INNER JOIN coffeemanager_cart_item ON product_id = tab1.id; 
        '''
    cursor = preparedStatements(query)
    drinks = dictfetchall(cursor)
    cursor.close()

    return render(request, "coffeemanager/viewCart.html", context={'drinks': drinks})

def view_cart(request):
    email = request.user.username
    query = f'''
        SELECT id FROM coffeemanager_cart WHERE customer_email = "{request.user.username}";
        '''
    cart_id = preparedStatements(query).fetchone()

    drinks = []
    if cart_id:
        cart_id = cart_id[0]
        query = f'''
            SELECT tab1.id, name, price, quantity FROM coffeemanager_drink AS tab1
            INNER JOIN coffeemanager_cart_item ON tab1.id = product_id
            WHERE cart_id = {cart_id}; 
            '''
        cursor = preparedStatements(query)
        drinks = dictfetchall(cursor)
        cursor.close()
    return render(request, "coffeemanager/viewCart.html", context={'drinks': drinks})

def submitOrder(request):    
    transaction_start = "START TRANSACTION;"
    preparedStatements(transaction_start)

    # Create a new order object in db
    # ORM Usage
    order = Orders(customer_id = request.user.username, order_status=False)
    order.save()
    commit = "COMMIT;"
    preparedStatements(commit)

    maxId = """
            SELECT MAX(id) FROM coffeemanager_orders
            """
    order_id = preparedStatements(maxId).fetchone()[0]
    
    # Fetch the current cart_id in the customer's account
    query = f'''
                SELECT id FROM coffeemanager_cart WHERE customer_email = "{request.user.username}";
            '''
    cart_id = preparedStatements(query).fetchone()[0]
    
    # Fetch all the items from the cart
    query = f'''
                SELECT id, product_id, quantity FROM coffeemanager_cart_item WHERE cart_id = {cart_id};
            '''
    cursor = preparedStatements(query)
    cart_items = dictfetchall(cursor)
    cursor.close()

    # Insert every item from the cart into the order item table
    for item in cart_items:
        # ORM Usage
        order_item = Order_Item(drink_id = item['product_id'], order_id = order_id, quantity = item['quantity'])
        order_item.save()
        commit = "COMMIT;"
        preparedStatements(commit)

        delete = f''' 
            DELETE FROM coffeemanager_cart_item
            WHERE id = {item['id']};
            '''
        preparedStatements(delete)
        commit = "COMMIT;"
        preparedStatements(commit)
        cnx.commit()
    
    # Delete cart object from database
    delete = f''' 
            DELETE FROM coffeemanager_cart
            WHERE customer_email = "{request.user.username}";
            '''
    preparedStatements(delete)
    commit = "COMMIT;"
    preparedStatements(commit)
    cnx.commit()

    return render(request, "coffeemanager/confirmation.html", context={'confirmation': order_id})

def order(request):
    customer_id = request.user.username
    drink_id = request.POST.get('drink_id')

    transaction_start = "START TRANSACTION;"
    preparedStatements(transaction_start)

    # ORM Usage
    order = Orders(customer_id=request.user.username, order_status=False)
    order.save()
    commit = "COMMIT;"
    preparedStatements(commit)
    maxId = """
            SELECT MAX(id) FROM coffeemanager_orders
            """
    order_id = preparedStatements(maxId).fetchone()[0]
    order_item = Order_Item(drink_id = drink_id, order_id = order_id, quantity = 1)
    order_item.save()
    commit = "COMMIT;"
    preparedStatements(commit)
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
    cart_id = f'''
            SELECT id FROM coffeemanager_cart
            WHERE customer_email = "{request.user.username}";
            '''
    cart_id = preparedStatements(cart_id).fetchone()

    if cart_id:
        cart_id = cart_id[0]
        delete = f''' 
                    DELETE FROM coffeemanager_cart_item
                    WHERE cart_id = {cart_id};
                    '''
        preparedStatements(delete)
        commit = "COMMIT;"
        preparedStatements(commit)
        cnx.commit()

        delete = f'''
                    DELETE FROM coffeemanager_cart
                    WHERE id = {cart_id}; 
                '''
        preparedStatements(delete)
        commit = "COMMIT;"
        preparedStatements(commit)
        cnx.commit()

    auth.logout(request)
    return redirect('home')

def status(request):
    customer_id = request.user.username
    query = f'''SELECT id, order_status from coffeemanager_orders where customer_id="{customer_id}";
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
    review = request.POST.get('temp')
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
        WHERE customer_id = "{customer_id}" order by review_id desc;
     '''
    cursor = preparedStatements(query)
    reviews = dictfetchall(cursor)
    cursor.close()
    return render(request, "coffeemanager/menu/myReviews.html", context={'reviews': reviews} )
  
def myPrevOrders(request):
    customer_id = request.user.username
    query = f'''SELECT id FROM coffeemanager_orders 
          WHERE order_status = TRUE AND customer_id = "{customer_id}" 
          ORDER BY id desc;
      '''
    cursor = preparedStatements(query)
    prev_orders = dictfetchall(cursor)
    cursor.close()
    return render(request, "coffeemanager/menu/myPrevOrders.html", context={'prevOrders': prev_orders})
  




