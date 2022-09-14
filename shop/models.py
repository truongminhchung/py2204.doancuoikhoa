from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=50)
    decription = models.TextField()
    category_parent = models.ForeignKey(
        'self',
        blank=True,
        null=True,
        on_delete=models.CASCADE
    )

    class Meta:
        db_table = "Category"

    def __str__(self):
        return self.name

class Brand(models.Model):
    name = models.CharField(max_length=50)
    decription = models.TextField()
    country = models.TextField()

    class Meta:
        db_table = "Brand"

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    price = models.IntegerField()
    stock_quantity = models.IntegerField()
    image = models.CharField(max_length=300, default='')
    detail = models.TextField()
    status = models.BooleanField(default=True)

    class Meta:
        db_table = "Product"

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE,)
    path = models.TextField()

    class Meta:
        db_table = "ProductImage"

class Promotion(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    discount = models.IntegerField()
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField()

    class Meta:
        db_table = "Promotion"


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    create_date = models.DateField(default=timezone.now)
    total_amount = models.IntegerField(default=True)
    phone = models.CharField(max_length=10)
    address = models.TextField()
    status = models.IntegerField(default=0)

    class Meta:
        db_table = "Order"

class OrderDetail(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    amout = models.IntegerField()

    class Meta:
        db_table = "OrderDetail"