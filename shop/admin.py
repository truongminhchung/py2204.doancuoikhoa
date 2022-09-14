from django.contrib import admin
from shop.models import Category, Brand, Product, ProductImage, Promotion, Order, OrderDetail


class CategoryAdmin(admin.ModelAdmin):
    list_display=('id', 'name', 'decription', 'category_parent')
admin.site.register(Category, CategoryAdmin)

class BrandAdmin(admin.ModelAdmin):
    list_display=('id', 'name', 'decription', 'country')
admin.site.register(Brand, BrandAdmin)

class ProductAdmin(admin.ModelAdmin):
    list_display=( 'name', 'id', 'category', 'brand', 'price', 'stock_quantity','image', 'detail', 'status')
admin.site.register(Product, ProductAdmin)

class ProductImageAdmin(admin.ModelAdmin):
    list_display=('id','product_id', 'product', 'path')
admin.site.register(ProductImage, ProductImageAdmin)

class PromotionAdmin(admin.ModelAdmin):
    list_display=('id','product', 'discount', 'start_date', 'end_date')
admin.site.register(Promotion, PromotionAdmin)
