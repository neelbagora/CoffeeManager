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

class Order(models.Model):
    order_id = models.DecimalField(max_digits=8, decimal_places=4)
    customer_id = models.DecimalField(max_digits=8, decimal_places=4)
    order_status = models.BooleanField(default=False)
    
    def __str__(self):
        return "Order ID: "+self.order_id+" Customer ID: "+self.customer_id+" Order Status: "+self.order_status
    

class OrderItem(models.Model):
    product_id = models.DecimalField(max_digits=8, decimal_places=4)
    quantity = models.DecimalField(max_digits=4, decimal_places=0)
    order_id = models.DecimalField(max_digits=8, decimal_places=4)
    
    def __str__(self):
        return "Product ID: "+self.product_id+" Quantity: "+self.quantity+" Order ID: "+self.order_id
    
class Review(models.Model):
    review_id = models.DecimalField(max_digits=8, decimal_places=4)
    numStars = models.DecimalField(max_digits=2, decimal_places=0)
    comment = models.CharField(max_length=2048)
    
    def __str__(self):
        return "Review ID: "+self.review_id+" Number of Stars: "+self.numStars+" Comment: "+self.comment
    
class Cart(models.Model):
    cart_id = models.DecimalField(max_digits=8, decimal_places=4)
    customer_email = models.CharField(max_length=45, primary_key=True)
    
    def __str__(self):
        return "Card ID: "+self.cart_id+" Customer Email: "+self.customer_email
    
class CartEntry(models.Model):
    cart_id = models.DecimalField(max_digits=8, decimal_places=4)
    product_id = models.DecimalField(max_digits=8, decimal_places=4)
    quantity = models.DecimalField(max_digits=4, decimal_places=0)
    
    def __str__(self):
        return "Cart ID: "+self.cart_id+" Product ID: "+self.product_id+" Quantity: "+self.quantity
    
