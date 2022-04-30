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

class OrderItem(models.Model):
    product_id = models.DecimalField(max_digits=8, decimal_places=4)
    quantity = models.DecimalField(max_digits=4, decimal_places=0)
    order_id = models.DecimalField(max_digits=8, decimal_places=4)
    
    def __str__(self):
        return "Product ID: "+self.product_id+" Quantity: "+self.quantity+" Order ID: "+self.order_id
