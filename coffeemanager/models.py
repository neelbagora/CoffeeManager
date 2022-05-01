from django.db import models

# Create your models here. These will replicate the table schema in the datatbase

class Customer(models.Model):
    name = models.CharField(max_length=45)
    email = models.CharField(max_length=45, primary_key=True)

    def __str__(self):
        return "Name: "+self.name+" Email: "+self.email


class Drink(models.Model):
    name = models.CharField(max_length=45)
    price = models.DecimalField(max_digits=8, decimal_places=4)

    def __str__(self):
        return "Name: "+self.name+" Price: "+self.price
    
class Review(models.Model):
    review_id = models.DecimalField(max_digits=8, decimal_places=4)
    numStars = models.DecimalField(max_digits=2, decimal_places=0)
    comment = models.CharField(max_length=2048)

    def __str__(self):
        return "Review ID: " + self.review_id + " Number of Stars: " + numStars + " Comment: " + comment

class Cart(models.Model):
    customer_email = models.CharField(max_length = 45)
    def __str__(self):
        return "Email: " + self.customer_email

class Cart_Item(models.Model):
    cart_id = models.BigIntegerField()
    product_id = models.BigIntegerField()
    quantity = models.IntegerField()
    def __str__(self):
        return "Cart ID: " + cart_id + " Product ID: " + product_id + " Quantity: " + quantity

class Orders(models.Model):
    customer_id = models.CharField(max_length = 45)
    order_status = models.BooleanField()
    def __str__(self):
        return "Customer ID: " + self.customer_email + " Fulfilled: " + status

class Order_Item(models.Model):
    order_id = models.BigIntegerField()
    drink_id = models.BigIntegerField()
    quantity = models.IntegerField()
    def __str__(self):
        return "Order ID: " + order_id + " Drink ID: " + drink_id + " Quantity: " + quantity
