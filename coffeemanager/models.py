from django.db import models


# Contains Database ORM Models. These will replicate the table schema in the datatbase

class Customer(models.Model):
    name = models.CharField(max_length=45)
    email = models.CharField(max_length=45, primary_key=True)

    def __str__(self):
        return "Name: " + self.name + " Email: " + self.email


class Drink(models.Model):
    name = models.CharField(max_length=45)
    price = models.DecimalField(max_digits=8, decimal_places=4)

    def __str__(self):
        return "Name: " + self.name + " Price: " + self.price


class Review(models.Model):
    customer_id = models.CharField(max_length=45)
    drink_id = models.IntegerField()
    review = models.CharField(max_length=2048)

    def __str__(self):
        return "Customer ID: " + self.customerId + " Drink ID" + self.drinkId + " Review: " + self.rev


class Shop(models.Model):
    shop_name = models.CharField(max_length=45)
    address = models.CharField(max_length=2048)
    phone_num = models.CharField(max_length=45)
    opening_time = models.CharField(max_length=8)
    closing_time = models.CharField(max_length=8)

    def __str__(self):
        return "Shop Name: " + self.shop_name + " Address: " + self.address + " Phone Number: " + self.phone_num + " Opening Time: " + self.opening_time + " Closing Time: " + self.closing_time


class Cart(models.Model):
    customer_email = models.CharField(max_length=45)

    def __str__(self):
        return "Email: " + self.customer_email


class Cart_Item(models.Model):
    cart_id = models.BigIntegerField()
    product_id = models.BigIntegerField()
    quantity = models.IntegerField()

    def __str__(self):
        return "Cart ID: " + cart_id + " Product ID: " + product_id + " Quantity: " + quantity


class Orders(models.Model):
    customer_id = models.CharField(max_length=45)
    order_status = models.BooleanField()

    def __str__(self):
        return "Customer ID: " + self.customer_email + " Fulfilled: " + status


class Order_Item(models.Model):
    order_id = models.BigIntegerField()
    drink_id = models.BigIntegerField()
    quantity = models.IntegerField()

    def __str__(self):
        return "Order ID: " + order_id + " Drink ID: " + drink_id + " Quantity: " + quantity
