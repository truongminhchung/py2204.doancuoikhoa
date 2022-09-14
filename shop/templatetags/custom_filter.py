from django import template
from shop.models import Product, Promotion, ProductImage, Order
from django.utils import timezone
register = template.Library()

@register.filter
def check_product_sale(product_id):
    try:
        product_in_promotion = Promotion.objects.get(
            product_id=product_id, # kiểm tra product_id có trong bảng promotion không!
            start_date__lte=timezone.now(), #ngày bắt đầu < ngày hiện tại
            end_date__gt=timezone.now()) #ngày kết thúc > ngày hiện tại
        return True
    except Promotion.DoesNotExist:
        return False


@register.filter
def get_price_sale(product_id):
    try:
        product_in_promotion = Promotion.objects.get(
            product_id=product_id, # kiểm tra product_id có trong bảng promotion không!
            start_date__lte=timezone.now(), #ngày bắt đầu < ngày hiện tại
            end_date__gt=timezone.now()) #ngày kết thúc > ngày hiện tại
        return int((1 - product_in_promotion.discount/100) * product_in_promotion.product.price)
    except Promotion.DoesNotExist:
        return ''
@register.filter
def get_product_discount(product_id):
    try:
        product_in_promotion = Promotion.objects.get(
            product_id=product_id, # kiểm tra product_id có trong bảng promotion không!
            start_date__lte=timezone.now(), #ngày bắt đầu < ngày hiện tại
            end_date__gt=timezone.now()) #ngày kết thúc > ngày hiện tại
        return product_in_promotion.discount
    except Promotion.DoesNotExist:
        return ''


@register.filter
def count_product_in_cart(logged_user):
    try:
        user_ordered = Order.objects.get(user=logged_user, status=0) #Đếm sp cho đơn hàng chưa thành công
        return sum([item.quantity for item in user_ordered.orderdetail_set.all()])
    except:
        return 0