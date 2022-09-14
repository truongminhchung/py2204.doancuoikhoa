from django.shortcuts import render, redirect, HttpResponseRedirect
from django.http.response import JsonResponse
from django.contrib.auth import authenticate, login, urls
from shop.forms import LoginForm, RegistrationFrom
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.contrib.humanize.templatetags.humanize import intcomma
from django.utils.timezone import now
from django.db.models import Min, Max
from .models import Category, Brand, Product, ProductImage, Order, OrderDetail, Promotion


def index(request):
    categories = Category.objects.filter(category_parent__isnull=True)
    brands = Brand.objects.all()
    products = Product.objects.all()
    min_price = products.aggregate(Min('price'))
    max_price = products.aggregate(Max('price'))

    # productimages = ProductImage_set.all()
    # print(productimages.path)
    category_display = ''
    brand_display = ''

    category_search = request.GET.get('category')
    if category_search:
        category_display = Category.objects.get(name=category_search)
        products = Product.objects.filter(category=category_display)

    brand_search = request.GET.get('brand')
    if brand_search:
        brand_display = Brand.objects.get(name=brand_search)
        products = Product.objects.filter(brand=brand_display)

    product_promotions = Promotion.objects.filter(
        start_date__lte=now(), #ngày bắt đầu < ngày hiện tại
        end_date__gt=now() #ngày kết thúc > ngày hiện tại
    )

    return render(
        request=request,
        template_name='index.html',
        context={
            'categories': categories,
            'brands': brands,
            'category_display': category_display,
            'brand_display': brand_display,
            'products': products,
            'min_price': min_price['price__min'],
            'max_price': max_price['price__max'],
            'product_promotions': product_promotions
        }

    )

@login_required(login_url='login_user')
def view_product(request, product_id):
    try:
        product_data = Product.objects.get(id=product_id)
        return render(
            request=request,
            template_name='product/product-details.html',
            context = {
                'product_data':product_data,
            }
        )
    except Product.DoesNotExist:
        return render(request=request, template_name='404.html')


def register_user(request):
    form_register = RegistrationFrom()
    if request.method == "POST":
        form_register = RegistrationFrom(request.POST)
        if form_register.is_valid():
            form_register.save()
            return redirect('login_user')
    return render(
        request = request,
        template_name = 'user/register.html',
        context={
            'form_register': form_register
        }
    )

def login_user(request):
    formlogin = LoginForm()
    message=""
    if request.method == "POST":
        formlogin = LoginForm(request.POST)
        if formlogin.is_valid():
            user = authenticate(
                username=formlogin.cleaned_data['username'],
                password=formlogin.cleaned_data['password'],
            )
            if user:
                # print(" đăng nhập thành công")
                login(request=request, user=user)
                if request.GET.get('next'):
                    return HttpResponseRedirect(request.GET['next'])
                return redirect('index')
            else:
                message= "username or password is incorrect"

    return render(
        request = request,
        template_name = 'user/login.html',
        context={
            'formlogin': formlogin,
            'message':message
        }
    )

@login_required(login_url='login_user')
def add_product_to_cart(request, product_id):
    try:
    # print("logged_user:", request.user)
        logged_user = request.user
        product_data = Product.objects.get(id=product_id)

        # Kiễm tra xem người dùnq có giỏ hàng nào chưa thành công (status =0)
        user_has_ordered = Order.objects.get(user=logged_user, status=0) #status =0 là chưa thành công

        #	Người dùng có 1 order chưa thành công.
        #	Chia 2 trường hợp
        #	Người dùng thêm 1 sản ghẩm không trùng với các có trong giò hàng. Thêm mới 1 dòng OrderDetail với sản phẩm mới


        # Người dùng thêm sản phầm trùng với sản phẩm đã có trong giỏ hàng. Cập nhập dòng OrderDetail với sản phẩm đó và tăng quantity lên lorder = user_has_ordered # Đối tên lại cho dể xử lý
        order = user_has_ordered
        orderdetail = OrderDetail.objects.get(order=order,product=product_data)
        # orderdetail = order.orderdetail_set.get(product=product_data) #(dùng quan hệ)
        #orderdetail = order.orderdetail_set.get
        # Qua dòng này thì đồng nghĩa là sản phẩm thêm mới trùng với 1 trong các sàn phẩm trong giỏ hàng.
        # Tăng quantity += 1
        orderdetail.quantity += 1
        orderdetail.amout = orderdetail.quantity * product_data.price
        orderdetail.save()

    except Product.DoesNotExist:
        pass
    except Order.DoesNotExist:
        new_order = Order.objects.create(
            user=logged_user,
            status=0,
            create_date=now(),
            total_amount=0,
            phone="",
            address="",
        )
        OrderDetail.objects.create(
            product=product_data,
            order=new_order,
            quantity=1,
            amout=product_data.price
        )
    except OrderDetail.DoesNotExist:
        #	Người dùng thêm 1 sản ghẩm không trùng với các có trong giò hàng. Thêm mới 1 dòng OrderDetail với sản phẩm mới
        OrderDetail.objects.create(
            product=product_data,
            order=order,
            quantity=1,
            amout=product_data.price
        )

    # return redirect('index')

    user_ordered = Order.objects.get(user=logged_user, status=0) #Đếm sp cho đơn hàng chưa thành công
    quantity = sum([item.quantity for item in user_ordered.orderdetail_set.all()])
    return JsonResponse({'quantity': quantity})

@login_required(login_url='login_user')
def change_product_quantity(request, action, product_id):
    logged_user = request.user
    product_data = Product.objects.get(id=product_id)
    order = Order.objects.get(user=logged_user, status=0)
    orderdetail = OrderDetail.objects.get(order=order,product=product_data)
    if action == "increase": #tăng
        orderdetail.quantity +=1
        orderdetail.amout = orderdetail.quantity * product_data.price
        orderdetail.save()

    else:
        # giảm
        if orderdetail.quantity == 1:
            orderdetail.delete()
        else:
            orderdetail.quantity -=1
            orderdetail.amout = orderdetail.quantity * product_data.price
            orderdetail.save()
    return redirect('show_cart')

@login_required(login_url='login_user')
def delete_product_in_cart(request, product_id):
    logged_user = request.user
    product_data = Product.objects.get(id=product_id)
    order = Order.objects.get(user=logged_user, status=0)
    orderdetail = OrderDetail.objects.get(order=order,product=product_data)
    orderdetail.delete()
    return redirect('show_cart')



@login_required(login_url='login_user')
def show_cart(request):
    orderdetail = []
    message = ""
    total_amount = 0
    try:
        logged_user = request.user
        order = Order.objects.get(user=logged_user, status=0)
        orderdetail = order.orderdetail_set.all()
        # print("orderdetail:", orderdetail )
        # print("độ dài:", len(orderdetail))

        # for item in orderdetail:
        #     print("tiền:", item.amout)

        if len(orderdetail) == 0:
            message = "Chưa có sản phẩm trong giỏ hàng"
        else:
            for item in orderdetail:
                total_amount = sum([item.amout for item in orderdetail])
    except:
        message = "Chưa có sản phẩm trong giỏ hàng"

    return render(
        request=request,
        template_name='cart/cart.html',
        context={
            'data_orderdetail': orderdetail,
            'message': message,
            'total_amount': total_amount,
        }
    )


@login_required(login_url='login_user')
def checkout(request):
    orderdetail = []
    total_amount = 0
    logged_user = request.user
    order = Order.objects.get(user=logged_user, status=0)
    orderdetail = order.orderdetail_set.all()
    if request.method == "POST":
        phone = request.POST['phone']
        address = request.POST['address']
        order.phone = phone
        order.address = address
        order.total_amount = sum([item.amout for item in orderdetail])
        order.status = 1 #đơn hàng thành công
        order.save()
        for od_detail in orderdetail:
            od_detail.product.stock_quantity -= od_detail.quantity
            od_detail.product.save()

        # sendmail
        from_email = settings.EMAIL_HOST_USER
        # subject = "Check out shop django"
        # message = f''' Hi {logged_user.username}
        # Thanks for you check out.
        # Total amount: {intcomma(order.total_amount)}đ
        # Thanhks,
        # dshop
        # '''
        text_content = 'This is an important message.'
        html_content = f'''
        Hi {logged_user.username}
        Thanks for you check out.
        <table class="table table-condensed">
				<thead>
					<tr class="cart_menu">
						<td class="description">Info</td>
						<td class="price">Price</td>
						<td class="quantity">Quantity</td>
						<td class="total">Total</td>
						<td></td>
					</tr>
				</thead>
				<tbody>'''
        for od_detail in orderdetail:
            html_content += f'''
            <tr>
                <td class="cart_description">
                    <h4>{ od_detail.product.name }</h4>
                </td>
                <td class="cart_price">
                    <p>{ intcomma(od_detail.product.price) }đ</p>
                </td>
                <td class="cart_quantity">
                    <div class="cart_quantity_button">
						{ od_detail.quantity }
					</div>
                </td>
                <td class="cart_total">
                    <p class="cart_total_price">{ intcomma(od_detail.amout) }đ</p>
                </td>
			</tr>
            '''
        html_content += f'''
				</tbody>
			</table>

        <p>Total amount: <b>{ intcomma(order.total_amount)} đ </b> </p>
        <p> Thanhks, </p>
        <p> dshop </p>
        '''

        recipient_list = [logged_user.email]
        # send_mail(subject, message, from_email, recipient_list)
        msg = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        return redirect('index')
    return render(
        request=request,
        template_name = 'cart/checkout.html',
        context={
            'data_orderdetail': orderdetail,
            'total_amount': total_amount,
        }
    )

