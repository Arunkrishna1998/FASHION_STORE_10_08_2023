import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMessage
from django.utils import timezone
from datetime import timedelta, datetime
from django.contrib.auth import login, logout, authenticate, get_user_model
import requests
from datetime import date
from django.views.decorators.cache import never_cache
from django.db.models import Q
import re

def index(request):
    product_list = Products.objects.all().filter(is_deleted=False,in_store=True)[:10]
    image = ProductImage.objects.all()
    context = {'product_list':product_list,'image':image}
    return render(request, 'store/index.html', context)


def product_details(request, product_id):
    product = Products.objects.get(uid=product_id)
    colors = ColorVariant.objects.filter(product_id=product_id)
    image_list = ProductImage.objects.all().filter(product=product)
    context = {'product':product,'colors':colors,'image_list':image_list}
    return render(request, 'store/product_details_2.html', context)


def size_list(request):
    color_id = request.GET['color_id']
    size_list = SizeVariant.objects.filter(Color_id=color_id)
    context = {'size_list':size_list}
    return render(request, 'store/more/size_list.html', context)


def show_price(request):
    size_id = request.GET['size_id']
    size = SizeVariant.objects.get(uid=size_id)
    context = {'price':size.price}
    return render(request, 'store/more/show_price.html', context)


#############################USER##########################################3

# from .forms import UserRegistrationForm
import random

from django.contrib.auth.models import User
from . models import Customer
def register(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        contact = request.POST['contact']
        if User.objects.filter(username=email).exists():
            messages.error(request, 'User With Email Already Exists')
            return render(request, 'user/register_1.html')


        password = str(random.randint(111111, 999999))
        user = User.objects.create_user(username=email,email=email,first_name=first_name.strip(),last_name=last_name.strip(),password=password)
        user.is_active = True
        user.save()
        Customer(user=user, email=user.email,contact=contact,otp=password).save()
        activateEmail(request, user, user.email, password)
        remaining_time = 120
        messages.info(request, f'Check {email} for OTP, Note: Check Spam too.')
        return render(request, 'user/signin_1.html', context={"username":user.email,'remaining_time': remaining_time})
    else:
        return render(request, 'user/register_1.html')


def category_list(request):
    category_list = Category.objects.all()
    context = {'category_list':category_list}
    return render(request, 'store/more/category_list.html', context)


def activateEmail(request, user, to_email,otp):
    mail_subject = "Login to your user account Using this OTP."
    message = render_to_string("mailbody/email_template.html", {
        'user': f'{user.first_name} {user.last_name}',
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': f'Your One Time Password is {otp}',
        "protocol": 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        pass
        # messages.success(request, f'Dear {user}, please go to you email {to_email} and check for the OTP \
        #         Note: Check your spam folder.')
    else:
        messages.error(request, f'Problem sending email to {to_email}, check if you typed it correctly.')


def validateOTP(request):
    if request.method == 'POST':
        otp = str(request.POST['otp'])
        email = request.POST['email']
        try:
            u_obj = User.objects.get(email=email)
            if u_obj.password == otp:
                u = User.objects.get(email=email)
                u.is_active = True
                u.save()
                username = u_obj.username
                user = authenticate(request, username=username, password=otp)
                if user is not None:
                    login(request, user)
                    return redirect('index')

            return redirect('signin')
        except Customer.DoesNotExist:
            return render(request, 'user/validateOTP.html', context={'email':email, 'msg':'Wrong OTP Try Again!'})


    return render(request, 'user/validateOTP.html')



from . forms import UserLogin,AdminLogin
def signin(request):
    if request.method == 'POST':
        email = request.POST['username']
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            password = str(random.randint(111111, 999999))
            user.set_password(password)
            user.save()
            activateEmail(request, user, user.email, password)
            messages.info(request,'OTP is Send To Your Email. Please Check')
            remaining_time = 120
            context = {'remaining_time': remaining_time,'username':email}
            return render(request, 'user/signin_1.html', context)
        else:
            messages.error(request, 'No User Exists')
            return render(request, 'user/signin_1.html')

    else:
        return render(request, 'user/signin_1.html')



def signin_confirmation(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = str(request.POST['password'])
        remaining_time = request.POST['remaining_time']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            try:
                cart = uCart.objects.get(cart_id=_cart_id(request))
                is_cart_item = CartItems.objects.filter(cart=cart).exists()
                total_existing = CartItems.objects.filter(cart=cart).aggregate(total_quantity=Sum('quantity'))[
                    'total_quantity']
                if total_existing is None:
                    total_existing = 0
                total_items = CartItems.objects.filter(user=user).aggregate(total_quantity=Sum('quantity'))[
                    'total_quantity']
                if total_items is None:
                    total_items = 0


                if is_cart_item:
                    if total_items < 10 and total_existing <= (10 - total_items):
                        cart_items = CartItems.objects.filter(cart=cart)
                        for item in cart_items:
                            item.user = user
                            item.save()

            except:
                pass

            try:
                guest = Guest.objects.get(guest_id=_wishlist_id(request))
                is_wish_list = WishList.objects.filter(guest=guest).exists()
                if is_wish_list:
                    wish_items = WishList.objects.filter(guest=guest)
                    for item in wish_items:
                        item.user = user
                        item.save()
            except:
                pass

            login(request, user)
            messages.success(request, 'Successfully Logged In')
            return redirect('index')
        else:
            messages.error(request, 'Invalid OTP')
            context = {'username': username,'remaining_time':remaining_time}
            return render(request, 'user/signin_1.html', context)

@login_required(login_url='login')
def customer_logout(request):
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "Logged out successfully!")
        return redirect("index")


def search_product(request, category=None):
    if request.method=='POST':
        query=request.POST['query']
        product_list = Products.objects.all().filter(is_deleted=False, in_store=True, slug__contains=query).order_by('uid')
        category_list = Category.objects.all()
        paginator = Paginator(product_list, 3)
        page = request.GET.get('page')
        paged_product = paginator.get_page(page)
        context = {'product_list': paged_product, 'category_list': category_list}
        return render(request, 'store/store.html', context)
    else:
        product_list = Products.objects.all().filter(in_store=True).order_by('uid')
        category_list = Category.objects.all()
        paginator = Paginator(product_list, 3)
        page = request.GET.get('page')
        paged_product = paginator.get_page(page)
        context = {'product_list': paged_product, 'category_list': category_list}
        return render(request, 'store/store.html', context)



def search_product_price(request):
    if request.method == 'POST':
        minValue = int(request.POST['minValue'])
        maxValue = int(request.POST['maxValue'])
        cartItems = 0
        print(minValue,maxValue)
        if minValue <= 0 & maxValue != 0:
            products = Products.objects.filter(price__lte=maxValue)
        elif maxValue <= 0 & minValue != 0:
            products = Products.objects.filter(price__gte=minValue)
        elif minValue >= 0 & maxValue >= 0:
            q_obj = Q(price__gte=minValue) & Q(price__lte=maxValue)
            products = Products.objects.filter(q_obj)
        elif minValue <= 0 & maxValue <= 0:
            q_obj = Q(price__gte=minValue) & Q(price__lte=maxValue)
            products = Products.objects.filter(q_obj)
        else:
            q_obj = Q(price__gte=minValue) | Q(price__lte=maxValue)
            products = Products.objects.filter(q_obj)

        context = {'products': products, 'cartItems': cartItems}
        return render(request, 'store/store.html', context)
########################################ADMIN##################################################################
from django.views.decorators.cache import cache_control
def admin_login(request):
    if request.method == 'POST':
        form = AdminLogin(request,request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            print(username,password)
            user = authenticate(request, username=username, password=password)
            if user is not None and user.is_staff == True:
                login(request, user)
                return redirect('admin_home')
            else:
                form.add_error(None, 'Invalid username or password')
        else:
                messages.error(request, 'Invalid username or password')
    else:
        form = AdminLogin()
    return render(request, 'admin_main/admin_login.html', {'form': form})


@login_required(login_url='admin_login')
def admin_home(request):
    if request.user.is_authenticated and request.user.is_superuser:
        now = timezone.now()
        week_start = now - timedelta(days=now.weekday())
        month_start = now.replace(day=1)
        year_start = now.replace(month=1, day=1)
        total_week = \
        Order.objects.filter(created_at__gte=week_start, created_at__lte=now).aggregate(total=Sum('order_total'))[
            'total']
        total_month = \
        Order.objects.filter(created_at__gte=month_start, created_at__lte=now).aggregate(total=Sum('order_total'))[
            'total']
        total_year = \
        Order.objects.filter(created_at__gte=year_start, created_at__lte=now).aggregate(total=Sum('order_total'))[
            'total']
        low_stock_items = SizeVariant.objects.filter(stock__lt=3)

        product_quantities = OrderProduct.objects.values('product').annotate(total_quantity=Sum('quantity'))
        sorted_products = product_quantities.order_by('-total_quantity')
        top_3_products = sorted_products[:3]
        product_list = Products.objects.all()

        # total_week = str(total_week)

        context = {
            'total_week': total_week,#round(float(total_week),3),
            'total_month': total_month,#round(float(total_month),3),
            'total_year': total_year,#,round(float(total_year),3),
            'low_stock_items':low_stock_items,
            'top_3_products':top_3_products,
            'product_list':product_list
        }
        return render(request, 'admin_main/admin_home.html', context)

    else:
        return redirect('admin_login')


# @login_required(login_url='admin_login')
def admin_logout(request):
    if request.user.is_superuser and request.user.is_authenticated:
        logout(request)
        messages.info(request, "Logged out successfully!")
        return redirect("admin_login")


def admin_change_password(request):
    if request.method == 'POST':
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        email = request.POST['email']
        if password1 == password2:
            user = User.objects.get(email=email)
            user.set_password(password1)
            user.save()
            messages.success(request, "Password Changed Successfully")
            return redirect('admin_login')
        else:
            messages.error(request, "Passwords Does not match")

    email = request.GET.get('email')
    token = request.GET.get('token')
    print(email,token)
    try:
        user = User.objects.get(username=email)
    except User.DoesNotExist:
        user = None

    token_generator = PasswordResetTokenGenerator()
    token_valid = user is not None and token_generator.check_token(user, token)

    if user and token_valid:
        context = {
            'email': email,
            'token': token,
        }
        return render(request, 'admin_main/forgot_password/forgot_password.html', context)
    else:
        return render(request, '404.html')



from django.contrib.auth.tokens import PasswordResetTokenGenerator
def passwordChangeEmail(request, user, to_email, token):
    token_generator = PasswordResetTokenGenerator()
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = token_generator.make_token(user)

    mail_subject = "Click On the link to Set new Password"
    message = render_to_string("admin_main/forgot_password/password_email.html", {
        'domain': get_current_site(request).domain,
        'uid': uid,
        'token': token,
        "protocol": 'https' if request.is_secure() else 'http',
        'email':user.email,
        'reset_link' : f"{request.scheme}://{request.get_host()}/admin_change_password/?email={user.email}&token={token}",
        'scheme':request.scheme,
        'host':request.get_host(),
    })

    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        request.session['otp_sent_timestamp'] = timezone.now().timestamp()
        # messages.success(request, f'Dear {user}, please go to your email {to_email} and check for the OTP. Note: Check your spam folder.')
    else:
        messages.error(request, f'Problem sending email to {to_email}, check if you typed it correctly.')

def get_link(request):
    if request.method == 'POST':
        email = request.POST['email']
        try:
            user = User.objects.get(email=email)
            passwordChangeEmail(request, user, user.email,user.password)
            messages.success(request, 'Check Your Email For Password Reset Link')
        except User.DoesNotExist:
            messages.error(request, 'Make Sure you enter a valid email')

    return render(request, 'admin_main/forgot_password/get_link.html')


@login_required(login_url='admin_login')
def admin_user_details_view(request):
    users_list = User.objects.exclude(is_staff=True)
    context = {'users_list':users_list}
    return render(request, 'admin_main/admin_user_details_view.html', context)

@login_required(login_url='admin_login')
def admin_user_details_search(request):
    if request.method=='POST':
        query = request.POST.get('query')
        users_list = User.objects.exclude(is_staff=True).filter(Q(first_name__contains=query) |
                                                                Q(last_name__contains=query) | Q(email__contains=query))
        context = {'users_list':users_list}
        return render(request, 'admin_main/admin_user_details_view.html', context)

@login_required(login_url='admin_login')
def admin_category_search(request):
    if request.method == 'POST':
        query = request.POST.get('query')
        preprocessed_query = slugify(query).replace(' ', '-')
        category_list = Category.objects.all().filter(Q(category_name__contains=query)|Q(slug__contains=query)|Q(slug__contains=preprocessed_query))
        context = {'category_list': category_list}
        return render(request, 'admin_main/categories.html', context)


@login_required(login_url='admin_login')
def admin_block_unblock(request):
    id = request.GET['id']
    user = User.objects.get(id=id)
    if user.is_active:
        user.is_active = False
        user.save()
        messages.info(request, "User Account Blocked")
    else:
        user.is_active = True
        user.save()
        messages.info(request, "User Account Unblocked")
    users_list = User.objects.exclude(is_staff=True)
    context = {'users_list':users_list}
    return render(request, 'admin_main/admin_user_details_view.html', context)

from . models import Category
from django.utils.text import slugify
@login_required(login_url='admin_login')
def admin_categories_add(request):
    if request.method == 'POST':
        try:
            category = request.POST.get('category')
            category = re.sub(r'\s+', ' ', category.strip())
            c = Category(category_name=category, slug=slugify(category))
            c.save()
            messages.info(request,"New Category added")
        except:
            messages.warning(request, "This Category may already exist")
        return redirect('categories')
    return render(request, 'admin_main/categories.html')

@login_required(login_url='admin_login')
def categories(request):
    category_list = Category.objects.all()
    context = {'category_list':category_list}
    return render(request, 'admin_main/categories.html', context)

@login_required(login_url='admin_login')
def admin_categories_edit(request):
    if request.method == 'POST':
        category = request.POST.get('category')
        id = request.POST.get('id')
        category = re.sub(r'\s+', ' ', category.strip())
        ctg = Category.objects.get(uid=id)
        ctg.category_name=category
        ctg.slug=slugify(category)
        ctg.save()
        return redirect('categories')
    else:
        id = request.GET['id']
        ctg = Category.objects.get(uid=id)
        edit = True
        category_list = Category.objects.all()
        context = {'ctg': ctg, 'edit':edit,'category_list':category_list}
        return render(request, 'admin_main/categories.html', context)


@login_required(login_url='admin_login')
def admin_categories_delete(request):
    id = request.GET['id']
    ctg = Category.objects.get(uid=id)
    if ctg.is_deleted == True:
        ctg.is_deleted = False
        ctg.save()
        messages.success(request, "Unblocked successfully!")
        return redirect('categories')
    ctg.is_deleted = True
    ctg.save()
    messages.error(request, "Blocked successfully!")
    return redirect('categories')

@login_required(login_url='admin_login')
def admin_products_view(request):
    products = Products.objects.all()
    context = {'products_list': products}
    return render(request, 'admin_main/product_lists.html', context)

@login_required(login_url='admin_login')
def admin_product_details_search(request):
    if request.method == 'POST':
        query = request.POST.get('query')
        products = Products.objects.filter(Q(product_name__contains=query)|Q(slug__contains=query))
        context = {'products_list': products}
        return render(request, 'admin_main/product_lists.html', context)

@login_required(login_url='admin_login')
def delete_product(request):
    product_id = request.GET['id']
    product = Products.objects.get(uid=product_id)
    product.is_deleted = True
    product.delete()
    return redirect('admin_products_view')


def admin_product_edit(request):
    pass


import numpy as np
import PIL
from .models import Category, ColorVariant, SizeVariant, Products, ProductImage
@login_required(login_url='admin_login')
def admin_product_add(request):
    if request.method == 'POST':
        product_name = request.POST.get('productname')
        product_price = request.POST.get('productprice')
        category_id = request.POST.get('category')
        image = request.FILES['image']
        product_description = request.POST.get('product_description')

        category = None
        if category_id:
            category = Category.objects.get(uid=category_id)
        product_name = product_name.strip()
        product_description = product_description.strip()

        product = Products.objects.create(
            product_name=product_name,
            price=product_price,
            rprice=product_price,
            category=category,
            product_description=product_description,
        )

        # new_width, new_height = 500, 500
        # img = Image.open(image)
        # img.thumbnail((new_width, new_height))
        # image_name = image.name
        # img_io = BytesIO()
        # img.save(img_io, format='JPEG')
        # image_file = ImageFile(img_io, name=image_name)
        print("****************************  1")

        new_width, new_height = 3024, 4032
        img = Image.open(image)
        img = img.resize((new_width, new_height), Image.LANCZOS)
        img_io = BytesIO()
        img.save(img_io, format='JPEG')
        image_name = image.name
        image_file = ImageFile(img_io, name=image_name)



        # product.image = image_file
        product.image = image_file
        product.save()
        messages.success(request, "Product Added To Store")
        return redirect('admin_product_add')
        # except:
        #     messages.error(request, "Couldn't Add Product To Store")

        return redirect('admin_product_add')


    categories = Category.objects.all().exclude(is_deleted=True)
    return render(request, 'admin_main/admin_product_add.html', {'category_list': categories})


import boto3
from botocore.exceptions import ClientError

def upload_image_to_s3(image, file_name, bucket_name='fashion_store-bucket', bucket_region='eu-north-1'):
    s3_client = boto3.client('s3', region_name=bucket_region)

    try:
        s3_client.upload_fileobj(image, bucket_name, file_name)
        s3_client.put_object_acl(Bucket=bucket_name, Key=file_name, ACL='public-read')
        image_url = f'https://{bucket_name}.s3.amazonaws.com/{file_name}'
        return image_url
    except ClientError as e:
        print(f"Error uploading image to S3: {e}")
        return None



from botocore.exceptions import ClientError
@login_required(login_url='admin_login')
def admin_product_details_update(request):
    if request.method == 'POST':
        product_id = request.POST['id']
        product_name = request.POST['productname']
        price = request.POST['productprice']
        product_description = request.POST['product_description']
        category_id = request.POST['category']

        product = Products.objects.get(uid=product_id)
        category = Category.objects.get(uid=category_id)


        product.product_name=product_name.strip()
        product.price=price
        product.product_description=product_description.strip()
        product.category=category
        product.save()
        try:
            image = request.FILES['image']
            file_name = image.name
            new_width, new_height = 500, 500
            img = Image.open(image)
            img.thumbnail((new_width, new_height))

            image_name = image.name
            img_io = BytesIO()
            img.save(img_io, format='JPEG')
            image_file = ImageFile(img_io, name=image_name)

            product.image = image_file
            product.save()


        except:
            pass

        messages.success(request, 'Details Updated')

        categories = Category.objects.all().filter(is_deleted=False)
        context = {'category_list': categories, 'product': product}
        return render(request, 'admin_main/admin_product_details_update.html', context)
    else:
        product_id = request.GET['id']
        product = Products.objects.get(uid=product_id)
        categories = Category.objects.all().filter(is_deleted=False)
        context = {'category_list': categories,'product':product}
        return render(request, 'admin_main/admin_product_details_update.html', context)

@login_required(login_url='admin_login')
def product_variants_view(request):
    product_id = request.GET['id']
    if product_id:
        product = Products.objects.get(uid=product_id)

    size_list = SizeVariant.objects.all()
    color_list = ColorVariant.objects.filter(product_id=product)
    context = {'product_id': product_id, 'color_list': color_list,'size_list':size_list}
    return render(request, 'admin_main/product_variants_view.html', context)

@login_required(login_url='admin_login')
def product_variants_add(request):
    if request.method == 'POST':
        product_id = request.POST['product_id']
        color = request.POST['color']
        size_l = request.POST.getlist('size[]')
        price_l = request.POST.getlist('price[]')
        stock_l = request.POST.getlist('stock[]')
        if product_id:
            product = Products.objects.get(uid=product_id)
        if ColorVariant.objects.filter(product_id=product,color=color).exists():
            color_id = ColorVariant.objects.get(product_id=product, color=color)
            for i in range(len(size_l)):
                if float(stock_l[i])>=0 and float(price_l[i])>0:
                    if SizeVariant.objects.filter(Color_id=color_id, size=size_l[i]).exists():
                        print('''SizeVariant.objects.filter(Color_id=color_id, size=size_l[i]).exists()''')
                        s = SizeVariant.objects.filter(Color_id=color_id, size=size_l[i]).first()
                        s.price = price_l[i]
                        s.stock = stock_l[i]
                        s.save()
                    else:
                        SizeVariant.objects.create(product_id=product,
                                                   Color_id=color_id,
                                                   size=size_l[i], price=price_l[i], stock=stock_l[i])
                else:
                    messages.info(request, "Couldn't update! Check if stock or price is valid")
                    size_list = SizeVariant.objects.all()
                    color_list = ColorVariant.objects.filter(product_id=product)
                    context = {'product_id': product_id, 'color_list': color_list, 'size_list': size_list}
                    return render(request, 'admin_main/product_variants_view.html', context)
        else:
            color_id = ColorVariant.objects.create(product_id=product,color=color)
            for i in range(len(size_l)):
                if float(stock_l[i]) >= 0 and float(price_l[i]) > 0:
                    SizeVariant.objects.create(product_id=product,
                                               Color_id=color_id,
                                               size=size_l[i],price=price_l[i],stock=stock_l[i])
                else:
                    color_id = ColorVariant.objects.get(color=color)
                    color_id.delete()
                    messages.info(request, "Couldn't update! Check if stock or price is valid")
                    size_list = SizeVariant.objects.all()
                    color_list = ColorVariant.objects.filter(product_id=product)
                    context = {'product_id': product_id, 'color_list': color_list, 'size_list': size_list}
                    return render(request, 'admin_main/product_variants_view.html', context)

        size_list = SizeVariant.objects.all()
        color_list = ColorVariant.objects.filter(product_id=product)
        context = {'product_id': product_id, 'color_list': color_list, 'size_list': size_list}
        return render(request, 'admin_main/product_variants_view.html', context)

    else:
        product_id = request.GET['id']
        if product_id:
            product = Products.objects.get(uid=product_id)

        size_list = SizeVariant.objects.all()
        color_list = ColorVariant.objects.filter(product_id=product)
        context = {'product_id': product_id, 'color_list': color_list, 'size_list': size_list}
        return render(request, 'admin_main/product_variants_view.html', context)


@login_required(login_url='admin_login')
def product_variants_stock_update(request,size_id,product_id):
    if product_id:
        product = Products.objects.get(uid=product_id)
    size_list = SizeVariant.objects.all()
    color_list = ColorVariant.objects.filter(product_id=product)
    if size_id:
        size = SizeVariant.objects.get(uid=size_id)
    update = True
    context = {'product_id': product_id,
               'color_list': color_list,
               'size_list': size_list,
               'size':size,
               'update':update}
    return render(request, 'admin_main/product_variants_view.html', context)


def product_variants_stock_delete(request,size_id,product_id):
    # product_id = request.GET['product_id']
    # size_id = request.GET['size_id']
    try:
        if size_id:
            size = SizeVariant.objects.get(uid=size_id)
            s = SizeVariant.objects.filter(Color_id=size.Color_id)
            if len(s) == 1:
                c = ColorVariant.objects.get(uid=size.Color_id.uid)
                c.delete()
            size.delete()
        messages.success(request, 'Details Deleted')
    except:
        pass

    product = Products.objects.get(uid=product_id)
    color_list = ColorVariant.objects.filter(product_id=product)
    size_list = SizeVariant.objects.all()
    ColorVariant.objects.filter(product_id=product)

    context = {'product_id': product_id, 'color_list': color_list, 'size_list': size_list}

    return render(request, 'admin_main/product_variants_view.html', context)


@login_required(login_url='admin_login')
def product_variants_stock_updates(request):
    if request.method == 'POST':
        product_id = request.POST['product_id']
        size_id = request.POST['size_id']
        price = request.POST['price']
        size = request.POST['size']
        stock = request.POST['stock']
        s = SizeVariant.objects.get(uid=size_id)
        s.price=price
        s.stock=stock
        s.size=size
        s.save()

        messages.success(request,'Details Updated')
        product = Products.objects.get(uid=product_id)
        color_list = ColorVariant.objects.filter(product_id=product)
        size_list = SizeVariant.objects.all()
        update = False
        context = {'product_id': product_id, 'color_list': color_list, 'size_list': size_list, 'size': size, 'update': update}
        return render(request, 'admin_main/product_variants_view.html', context)


@login_required(login_url='admin_login')
def variants_stock_update_cancel(request, product_id):
    if product_id:
        product = Products.objects.get(uid=product_id)

    size_list = SizeVariant.objects.all()
    color_list = ColorVariant.objects.filter(product_id=product)
    context = {'product_id': product_id, 'color_list': color_list, 'size_list': size_list}
    return render(request, 'admin_main/product_variants_view.html', context)

    size_list = SizeVariant.objects.all()
    color_list = ColorVariant.objects.filter(product_id=product)
    context = {'product_id': product_id, 'color_list': color_list, 'size_list': size_list}
    return render(request, 'admin_main/product_variants_view.html', context)


@login_required(login_url='admin_login')
def product_variant_images(request,color):
    image_list = ProductImage.objects.filter(Color_id = color)
    context = {'image_list': image_list,'color':color}
    return render(request, 'admin_main/product_variant_images.html', context)


import os
from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest



def resize_image(image_file_path):
    img = Image.open(image_file_path)
    fixed_width = 100
    fixed_height = 100
    resized_img = img.resize((fixed_width, fixed_height), Image.ANTIALIAS)
    resized_img.save(image_file_path)


from PIL import Image
from django.core.files.images import ImageFile
from io import BytesIO
def product_variant_images_add(request):
    if request.method == 'POST':
        color_id = request.POST.get('color')
        product_images = request.FILES.getlist('image_list[]')

        try:
            color = ColorVariant.objects.get(uid=color_id)

            for image in product_images:
                product_image = ProductImage(product=color.product_id, Color_id=color)

                # new_width, new_height = 500, 500
                # img = Image.open(image)
                # img.thumbnail((new_width, new_height))
                # image_name = image.name
                # img_io = BytesIO()
                # img.save(img_io, format='JPEG')
                # image_file = ImageFile(img_io, name=image_name)

                new_width, new_height = 3024, 4032
                img = Image.open(image)
                img = img.resize((new_width, new_height), Image.LANCZOS)
                img_io = BytesIO()
                img.save(img_io, format='JPEG')
                image_name = image.name
                image_file = ImageFile(img_io, name=image_name)

                product_image.image = image_file
                product_image.save()

            image_list = ProductImage.objects.filter(Color_id=color_id)
            context = {'image_list': image_list, 'color': color_id}
            return render(request, 'admin_main/product_variant_images.html', context)

        except ColorVariant.DoesNotExist:
            return HttpResponseBadRequest("ColorVariant does not exist.")

    return HttpResponseBadRequest("Invalid request method.")


def product_image_delete(request, image_id,color):
    image = get_object_or_404(ProductImage, uid=image_id)

    image_file_path = os.path.join(settings.MEDIA_ROOT, image.image.name)
    if os.path.exists(image_file_path):
        try:
            os.remove(image_file_path)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    image.delete()
    return redirect('product_variant_images', color=color)

@login_required(login_url='admin_login')
def admin_product_update(request):
    if request.method == 'POST':
        product_name = request.POST.get('productname')
        product_price = request.POST.get('productprice')
        category_id = request.POST.get('category')
        product_description = request.POST.get('product_description')
        color_variants = request.POST.getlist('color_variant[]')
        color_prices = request.POST.getlist('color_price[]')
        size_variants = request.POST.getlist('size_variant[]')
        size_prices = request.POST.getlist('size_price[]')

        color_quantity = request.POST.getlist('color_quantity[]')
        size_quantity = request.POST.getlist('size_quantity[]')

        product_images = request.FILES.getlist('product_images[]')
        id = request.POST['id']

        category = None
        if category_id:
            category = Category.objects.get(uid=category_id)

        product = Products.objects.get(uid=id)
        product.product_name=product_name
        product.price=product_price
        product.rprice=product_price
        product.category=category
        product.product_description=product_description
        product.save()
        # image=pic

        for i in range(len(color_variants)):
            color_variant = ColorVariant.objects.create(
                color_name=color_variants[i],
                price=color_prices[i],
                quantity=color_quantity[i]
            )
            product.color_variant.add(color_variant)

        for i in range(len(size_variants)):
            size_variant = SizeVariant.objects.create(
                size_name=size_variants[i],
                price=size_prices[i],
                quantity = size_quantity[i]
            )
            product.size_variant.add(size_variant)
        return redirect('admin_product_update')

    categories = Category.objects.all()
    id = request.GET['id']
    product = Products.objects.get(uid=id)
    return render(request, 'admin_main/admin_product_update.html', {'category_list': categories,'product':product})

def add_remove_product_to_store(request, product_id):
    if product_id:
        product = Products.objects.get(uid=product_id)
        if product.in_store == False:
            c = ColorVariant.objects.filter(product_id=product_id)
            s = ColorVariant.objects.filter(product_id=product_id)
            i = ProductImage.objects.filter(product=product)
            if len(c)!=0 and len(s)!=0 and len(i)!=0:
                # product.is_deleted = False
                product.in_store=True
                product.save()
                messages.success(request, 'Product is Added to Store.')
            else:
                messages.info(request, 'Product Can not be added to store, Please check if Variants and Images are added.')
        else:
            c = ColorVariant.objects.filter(product_id=product_id)
            s = ColorVariant.objects.filter(product_id=product_id)
            i = ProductImage.objects.filter(product=product)
            if len(c) != 0 and len(s) != 0 and len(i) != 0:
                # product.is_deleted = False
                product.in_store = False
                product.save()
                messages.info(request, 'Product is Removed from Store.')

    return redirect('admin_products_view')


@login_required(login_url='admin_login')
def admin_order_details_view(request):
    order_list = Order.objects.filter(is_ordered=True).order_by('-created_at')
    context = {'order_list':order_list}
    return render(request, 'admin_main/admin_order_details_view.html',context)

@login_required(login_url='admin_login')
def admin_order_info_view(request,order):
    order = Order.objects.get(id=order)
    order_details = OrderProduct.objects.filter(order=order)
    context = {'order_details':order_details,'order':order}
    return render(request, 'admin_main/admin_order_info_view.html',context)


@login_required(login_url='admin_login')
def order_status_update(request):
    if request.method == 'POST':
        id = request.POST['id']
        status = request.POST.get('status')
        if status is None:
            messages.warning(request, 'Order Status Can not be Updated')
            return redirect('admin_order_info_view', order=id)

        order = Order.objects.get(id=id)
        order.status=status
        order.save()
        messages.success(request, 'Order Status Updated')
        return redirect('admin_order_info_view', order=order.id)

############################################################################################################


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


from . models import uCart, CartItems
def add_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        size_id = request.POST.get('size_id')
        quantity = int(request.POST.get('quantity'))
        if request.user.is_authenticated:
            total_items = CartItems.objects.filter(user=request.user).aggregate(total_quantity=Sum('quantity'))['total_quantity']
            if total_items is None:
                total_items = 0
            if total_items > 10:
                messages.warning(request, f'Cart Limit Reached You already have {total_items} in Your cart and you can add {10-total_items} items')
                return redirect('product_details', product_id=product_id)
            if size_id:
                product = Products.objects.get(uid=product_id)
                variant = SizeVariant.objects.get(uid=size_id)
                try:
                    total_items = CartItems.objects.filter(user=request.user).aggregate(total_quantity=Sum('quantity'))[
                        'total_quantity']
                    if total_items is None:
                        total_items = 0
                    if total_items + quantity > 10:
                        messages.warning(request,
                                         f'Cart Limit Reached You already have {total_items} items '
                                         f'in Your cart and you can add {10 - total_items} items')

                        return redirect('product_details', product_id=product_id)
                    cart_item = CartItems.objects.get(product_variant=variant, user=request.user)
                    if variant.stock > quantity:
                        variant.stock -= quantity
                        cart_item.quantity += quantity
                        cart_item.save()
                        variant.save()
                        messages.success(request, 'Product Added to cart ')
                        return redirect('product_details', product_id=product_id)
                    else:
                        messages.info(request, 'Product Out of stock ')
                        return redirect('product_details', product_id=product_id)
                except CartItems.DoesNotExist:
                    if variant.stock > quantity:
                        variant.stock -= quantity
                        cart_item = CartItems.objects.create(product=product,
                                                             quantity=quantity,
                                                             user=request.user,
                                                             product_variant=variant)
                        variant.save()
                        cart_item.save()
                    else:
                        messages.info(request, 'Product Out of stock ')
                        return redirect('product_details', product_id=product_id)
                return redirect('cart')
            else:
                messages.error(request, 'Please Select a Color and Size')
                return redirect('product_details', product_id=product_id)
        else:
            if size_id:
                product = Products.objects.get(uid=product_id)
                variant = SizeVariant.objects.get(uid=size_id)
                try:
                    cart = uCart.objects.get(cart_id=_cart_id(request))
                except uCart.DoesNotExist:
                    cart = uCart.objects.create(cart_id=_cart_id(request))
                cart.save()

                total_items = CartItems.objects.filter(cart=cart).aggregate(total_quantity=Sum('quantity'))['total_quantity']
                if total_items is None:
                    total_items = 0
                if total_items > 10:
                    messages.warning(request,
                        f'Cart Limit Reached You already have {total_items} in Your cart and you can add {10 - total_items} items')
                    return redirect('product_details', product_id=product_id)

                try:

                    total_items = CartItems.objects.filter(cart=cart).aggregate(total_quantity=Sum('quantity'))[
                        'total_quantity']
                    if total_items is None:
                        total_items = 0
                    if total_items+quantity > 10:
                        messages.warning(request,
                                         f'Cart Limit Reached You already have {total_items} items '
                                         f'in Your cart and you can add {10 - total_items} items')

                        return redirect('product_details', product_id=product_id)
                    cart_item = CartItems.objects.get(product_variant=variant, cart=cart)
                    if variant.stock > quantity:
                        variant.stock -= quantity
                        cart_item.quantity += quantity
                        cart_item.save()
                        variant.save()

                    else:
                        messages.info(request, 'Product Out of stock ')
                        return redirect('product_details', product_id=product_id)
                except CartItems.DoesNotExist:
                    if variant.stock > quantity:
                        variant.stock -= quantity
                        cart_item = CartItems.objects.create(product=product,
                                                             quantity=quantity,
                                                             cart=cart,
                                                             product_variant=variant)
                        variant.save()
                        cart_item.save()
                    else:
                        messages.info(request, 'Product Out of stock ')
                        messages.error(request, 'Please Select a Color and Size')
            else:
                messages.error(request,'Please Select a Color and Size')
                return redirect('product_details', product_id=product_id)

            messages.success(request, 'Product Added to Cart')
            return redirect('product_details', product_id=product_id)

def add_to_cart_1(request):
    product_id = request.GET['product_id']
    size_id = request.GET['size_id']
    product = Products.objects.get(uid=product_id)
    variant = SizeVariant.objects.get(uid=size_id)
    if request.user.is_authenticated:
        try:
            cart_item = CartItems.objects.get(product_variant=variant, user=request.user)
            if variant.stock > 0:
                variant.stock -= 1
                cart_item.quantity += 1
                cart_item.save()
                variant.save()
            else:
                messages.info(request, 'Product Out of stock Available')
        except CartItems.DoesNotExist:
            cart = uCart.objects.get(cart_id=request.user)
            cart_item = CartItems.objects.create(product=product, quantity=1, cart=cart, product_variant=size_id)
            variant.stock -= 1
            variant.save()
            cart_item.save()
        return redirect('cart')
    else:
        cart = uCart.objects.get(cart_id=_cart_id(request))
        try:
            cart_item = CartItems.objects.get(product_variant=size_id, cart=cart)
            if variant.stock>0:
                variant.stock -= 1
                cart_item.quantity += 1
                cart_item.save()
                variant.save()
            else:
                messages.info(request, 'Product Out of stock Available')
        except CartItems.DoesNotExist:
            cart_item = CartItems.objects.create(product=product, quantity=1, cart=cart, product_variant=size_id)
            variant.stock -= 1
            variant.save()
            cart_item.save()
        return redirect('cart')



def remove_from_cart(request):
    item_id = request.GET['item_id']
    item = CartItems.objects.get(id=item_id)
    item.delete()
    messages.success(request, 'Product Removed From Cart')
    return redirect('cart')



def inc_cart_item(request, item_id):
    item = CartItems.objects.get(id=item_id)
    size = SizeVariant.objects.get(uid=item.product_variant.uid)
    total = 0
    quantity = 0
    try:
        cart_items = CartItems.objects.filter(user=request.user, is_active=True)
        total_existing = CartItems.objects.filter(user=request.user, is_active=True).aggregate(total_quantity=Sum('quantity'))[
            'total_quantity']
    except:
        cart = uCart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItems.objects.filter(cart=cart, is_active=True)

        total_existing = CartItems.objects.filter(cart=cart).aggregate(total_quantity=Sum('quantity'))[
            'total_quantity']

    if total_existing is None:
        total_existing = 0
    if total_existing>=10:
        # messages.info(request, 'You can Only Put 10 items to Cart at a time')
        for cart_item in cart_items:
            total += (cart_item.product_variant.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total) / 100
        grant_total = total + tax


        return JsonResponse({
            'price': item.product_variant.price,
            'quantity': item.quantity,
            'total': total,
            'grant_total': grant_total,
            'tax': tax,
            'total_existing': total_existing,
        })

    if size.stock >= 1:
        size.stock -= 1
        size.save()
        item.quantity += 1
        item.save()

        for cart_item in cart_items:
            total += (cart_item.product_variant.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total) / 100
        grant_total = total + tax

        print("total_existing =================== ",total_existing)

        return JsonResponse({
            'price': item.product_variant.price,
            'quantity': item.quantity,
            'total': total,
            'grant_total': grant_total,
            'tax': tax,
            'total_existing': total_existing,
        })
    else:
        return JsonResponse({'error': 'Product out of Stock'})

def dec_cart_item(request, item_id):
    item = CartItems.objects.get(id=item_id)
    size = SizeVariant.objects.get(uid=item.product_variant.uid)

    total = 0
    quantity = 0
    total_existing = 0
    try:
        cart_items = CartItems.objects.filter(user=request.user, is_active=True)
    except:
        cart = uCart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItems.objects.filter(cart=cart, is_active=True)

    # cart_items = CartItems.objects.filter(user=request.user, is_active=True)
    if item.quantity > 1:
        size.stock += 1
        size.save()
        item.quantity -= 1
        item.save()
        for cart_item in cart_items:
            total += (cart_item.product_variant.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total) / 100
        grant_total = total + tax


        return JsonResponse({
            'price':item.product_variant.price,
            'quantity': item.quantity,
            'total': total,
            'grant_total': grant_total,
            'tax': tax,

        })
    else:
        size.stock += 1
        size.save()
        item.delete()
        return JsonResponse({'removed': True})



def remove_from_cart_1(request):
    product_id = request.GET['product_id']
    size_id = request.GET['size_id']
    print("*********************REMOVE FROM CART*************************")
    product = Products.objects.get(uid=product_id)
    variant = SizeVariant.objects.get(uid=size_id)
    print("*******************",request.user)
    if request.user.is_authenticated:
        try:
            cart_item = CartItems.objects.get(product_variant=size_id, user=request.user)

            variant.stock += 1
            cart_item.quantity -= 1
            cart_item.save()
            variant.save()

            if cart_item.quantity == 0:
                cart_item.delete()
        except CartItems.DoesNotExist:
            return redirect('cart')

        return redirect('cart')
    else:
        cart = uCart.objects.get(cart_id=_cart_id(request))
        try:
            # variant = SizeVariant.objects.get(uid=size_id)
            cart_item = CartItems.objects.get(product_variant=size_id, cart=cart)

            variant.stock += 1
            cart_item.quantity -= 1
            cart_item.save()
            variant.save()

            if cart_item.quantity == 0:
                cart_item.delete()
        except CartItems.DoesNotExist:
            return redirect('cart')

        return redirect('cart')


def cart(request,total=0,quantity=0,cart_items=None):
    tax=0
    grant_total=0
    try:
        if request.user.is_authenticated:
            cart_items = CartItems.objects.filter(user=request.user, is_active=True)
        else:
            cart = uCart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItems.objects.filter(cart=cart, is_active=True)

        for cart_item in cart_items:
            total += (cart_item.product_variant.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2*total)/100
        grant_total = total+tax
    except:
        pass

    size_variant = SizeVariant.objects.all()
    color_variant = ColorVariant.objects.all()
    context = {'total':total,
               'quantity':quantity,
               'cart_items':cart_items,
               'size_variant':size_variant,
               'color_variant':color_variant,
               'tax':tax,
               'grant_total':grant_total
               }
    return render(request, 'store/cart_1.html', context)


from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
def view_store(request,category=None):
    if category != None:
        c = Category.objects.get(slug=category)
        product_list = Products.objects.all().filter(is_deleted=False,in_store=True,category=c).order_by('uid')
        category_list = Category.objects.all()
        paginator = Paginator(product_list, 3)
        page = request.GET.get('page')
        paged_product = paginator.get_page(page)
        minprice,maxprice = 0,10000
        context = {'product_list': paged_product, 'category_list': category_list,
                   'minprice':minprice,'maxprice':maxprice}
        return render(request, 'store/store.html', context)
    else:
        product_list = Products.objects.all().filter(in_store=True).order_by('uid')
        category_list = Category.objects.all()
        paginator = Paginator(product_list,6)
        page=request.GET.get('page')
        paged_product = paginator.get_page(page)
        minprice, maxprice = 0, 10000
        context = {'product_list':paged_product, 'category_list':category_list,
                   'minprice':minprice,'maxprice':maxprice}
        return render(request, 'store/store.html', context)



def filter_products(request):
    pass

@login_required(login_url='login')
def user_dashboard(request):
    if request.user.is_authenticated:
        orders = Order.objects.filter(user=request.user).order_by('-id')
        context = {'orders':orders}
        return render(request, 'user/user_dashboard_1.html', context)

@login_required(login_url='login')
def user_order_details(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-id')
    context = {'orders': orders}
    return render(request, 'user/user_order_details.html', context)

@login_required(login_url='login')
def checkout(request,total=0,quantity=0,cart_items=None):
    if request.user.is_authenticated:

        check_cart_items = CartItems.objects.filter(user=request.user, is_active=True)
        if check_cart_items is None or len(check_cart_items) == 0:
            messages.warning(request, 'Cart is Empty')
            return redirect('cart')

        try:
            cart_items = CartItems.objects.filter(user=request.user,is_active=True)
            for cart_item in cart_items:
                total += (cart_item.product_variant.price * cart_item.quantity)
                quantity += cart_item.quantity

            tax = (2 * total) / 100
            grant_total = total + tax
        except:
            pass

        size_variant = SizeVariant.objects.all()
        color_variant = ColorVariant.objects.all()

        yr = int(datetime.date.today().strftime('%Y'))
        dt = int(datetime.date.today().strftime('%d'))
        mt = int(datetime.date.today().strftime('%m'))
        d = datetime.date(yr, mt, dt)
        cur_date = d.strftime('%Y%m%d')
        address_list = ShippingAddress.objects.filter(user=request.user)

        context = {'total':total,
                   'quantity':quantity,
                   'cart_items':cart_items,
                   'size_variant':size_variant,
                   'color_variant':color_variant,
                   'address_list':address_list,
                    'tax':tax,
                   'grant_total':grant_total
                   }
        return render(request, 'user/checkout_1.html', context)
    else:
        return redirect('login')

@login_required(login_url='login')
def load_address(request,total=0,quantity=0,cart_items=None):
    if request.user.is_authenticated:
        try:
            cart_items = CartItems.objects.filter(user=request.user,is_active=True)
            for cart_item in cart_items:
                total += (cart_item.product.price * cart_item.quantity)
                quantity += cart_item.quantity
        except:
            pass

        size_variant = SizeVariant.objects.all()
        color_variant = ColorVariant.objects.all()

        yr = int(datetime.date.today().strftime('%Y'))
        dt = int(datetime.date.today().strftime('%d'))
        mt = int(datetime.date.today().strftime('%m'))
        d = datetime.date(yr, mt, dt)
        cur_date = d.strftime('%Y%m%d')
        address_list = ShippingAddress.objects.filter(user=request.user)
        address_id = request.GET.get('address_id')
        address=None
        if address_id != 0:
            address = ShippingAddress.objects.filter(id=address_id)
        print(address)
        context = {'total':total,
                   'quantity':quantity,
                   'cart_items':cart_items,
                   'size_variant':size_variant,
                   'color_variant':color_variant,
                   'address_list':address_list,
                   'address': address
                   }
        return render(request, 'user/checkout.html', context)
    else:
        return redirect('login')


from . models import Order, Payment, OrderProduct
from . forms import OrderForm
import datetime
@login_required(login_url='login')
def place_order(request, total=0,quantity=0):
    cur_user = request.user
    cart_items = CartItems.objects.filter(user=cur_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        messages.warning(request, 'Your Cart is Empty!')
        return redirect('view_store')

    grant_total = 0
    tax = 0
    total,quantity=0,0
    total_1,quantity_1 =0,0

    for cart_item in cart_items:
        total_1 += (cart_item.product_variant.price * cart_item.quantity)
        quantity_1 += cart_item.quantity
    tax_1 = (2*total_1)/100
    grant_total_1=total_1+tax_1
    try:
        address = ShippingAddress.objects.get(user=request.user, is_default=True)
    except:
        messages.info(request, 'No Address Present or Selected,Please Add Address and Comeback before placing order')
        return redirect('checkout')

    if request.method == 'POST':
        form = OrderForm(request.POST)
        payment = Payment.objects.create(
            user=request.user,
            payment_method = 'cod',
        )
        payment.save()

        data = Order()
        data.user=request.user
        data.first_name = address.first_name
        data.last_name = address.last_name#form.cleaned_data['last_name']
        data.phone = address.phone
        data.email = address.email
        data.address_line_1 = address.address_line_1
        data.address_line_2 = address.address_line_2
        data.country = address.country
        data.state = address.state
        data.city = address.city
        data.pincode = address.pincode
        data.order_total = grant_total_1
        data.tax = tax_1
        data.ip = request.META.get('REMOTE_ADDR')
        data.payment = payment
        data.is_ordered = False
        data.save()

        #Generating Order Number
        yr = int(datetime.date.today().strftime('%Y'))
        dt = int(datetime.date.today().strftime('%d'))
        mt = int(datetime.date.today().strftime('%m'))
        d = datetime.date(yr,mt,dt)
        cur_date = d.strftime('%Y%m%d')
        order_number = cur_date + str(data.id)
        data.order_number = order_number
        data.save()

        for item in cart_items:
            order_product=OrderProduct.objects.create(
                user=request.user,
                product=item.product,
                product_price=(item.product_variant.price * item.quantity),
                quantity=item.quantity,
                size=item.product_variant.size,
                payment=payment,
                color=item.product_variant.Color_id.color,
                order=data
            )
            order_product.save()

        order = Order.objects.get(user=cur_user, order_number=order_number)
        order_items = OrderProduct.objects.filter(order=order)
        # quantity = 0
        for item in order_items:
            total += item.product_price
            quantity += item.quantity
        tax = (2*total)/100
        grant_total=total+tax
        context = {
            'order': order,
            'order_items': order_items,
            'total': total,
            'tax': order.tax,
            'grand_total': order.order_total,
        }
        return render(request, 'user/payment_1.html', context)
    # else:
    #     return redirect(request, "checkout")

@login_required(login_url='login')
def cash_on_delivery(request, order_id):
    cur_user = request.user
    order = Order.objects.get(id=order_id)
    order.is_ordered = True
    order.save()
    context = {'order':order}
    return render(request, 'user/cash_on_delivery_confirm.html', context)

@login_required(login_url='login')
def payments(request,orderno=0):
    print('ORDERNO: ', orderno)
    cur_user = request.user
    order = None
    order_items = None
    total = 0
    try:
        order = Order.objects.get(user=cur_user, id=orderno)
        order_items = OrderProduct.objects.filter(order=order)
        quantity = 0
        for item in order_items:
            total += item.product_price
            quantity += item.quantity


    except:
        order = Order.objects.filter(user=cur_user, is_ordered=True, id=orderno).first()

    context = {
        'order': order,
        'order_items': order_items,
        'total': total,
        'tax': order.tax if order else 0,
        'grand_total': order.order_total if order else 0,
    }
    return render(request, 'user/payment_1.html', context)



def OrderConfirmationEmail(request, user, to_email):
    mail_subject = "Login to your user account Using this OTP."
    message = render_to_string("user/order_confirmation_email.html", {
        'user': f'{user.first_name} {user.last_name}',

    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.success(request, f'Dear {user}, please go to you email {to_email} and check for the OTP \
                Note: Check your spam folder.')
        request.session['otp_sent_timestamp'] = timezone.now().timestamp()
    else:
        messages.error(request, f'Problem sending email to {to_email}, check if you typed it correctly.')


@login_required(login_url='login')
def order_details(request, orderno):
    order = Order.objects.get(id=orderno)
    print(order)
    order_product_list = OrderProduct.objects.filter(order=order)
    context = {'order_product_list':order_product_list,'orderno':orderno,'order':order}
    return render(request, 'user/order_details.html', context)

@login_required(login_url='login')
def cancel_order(request, orderno):
    order = Order.objects.get(id=orderno)
    order.status = 'Cancelled'
    order.save()
    messages.info(request, 'Order Cancelled')
    return redirect('order_details',orderno=orderno)


from . models import Coupons
@login_required(login_url='admin_login')
def admin_coupons_view(request):
    if request.user.is_authenticated and request.user.is_superuser:
        coupons_list = Coupons.objects.all()
        context = {'coupons_list':coupons_list}
        return render(request, 'admin_main/admin_manage_coupons.html',context)

@login_required(login_url='admin_login')
def admin_coupons_add(request):
    if request.user.is_authenticated and request.user.is_superuser:
        coupon_code = request.POST.get('coupon_code')
        MinPurchase = request.POST.get('MinPurchase')
        ExpDate = request.POST.get('ExpDate')
        amount = request.POST.get('amount')
        coupon_type = request.POST.get('coupon_type')
        if Coupons.objects.filter(coupon_code=coupon_code).exists():
            messages.warning(request, "Coupon Code is not Unique!")
            return redirect('admin_coupons_view')

        coupon = Coupons(coupon_code=coupon_code,
                         MinPurchase=MinPurchase,
                         ExpDate=ExpDate,
                         amount=amount,
                         coupon_type=coupon_type)
        coupon.save()
        messages.success(request, "New Coupon Added")
        return redirect('admin_coupons_view')


@login_required(login_url='admin_login')
def admin_coupons_update(request):
    if request.user.is_authenticated and request.user.is_superuser:
        if request.method == 'POST':
            coupon_code = request.POST.get('coupon_code')
            MinPurchase = request.POST.get('MinPurchase')
            ExpDate = request.POST.get('ExpDate')
            amount = request.POST.get('amount')
            coupon_id = request.POST.get('coupon_id')
            coupon_type = request.POST.get('coupon_type')

            coupon = Coupons.objects.get(id=coupon_id)
            coupon.coupon_code=coupon_code
            coupon.MinPurchase=MinPurchase
            coupon.ExpDate=ExpDate
            coupon.amount=amount
            coupon.coupon_type=coupon_type
            coupon.save()
            messages.success(request, "Coupon Details Updated")
            return redirect('admin_coupons_view')
        else:
            coupon_id = request.GET.get('coupon_id')
            coupon=Coupons.objects.get(id=coupon_id)
            coupons_list = Coupons.objects.all()
            edit = True
            context = {'coupons_list': coupons_list, 'coupon':coupon, 'edit':edit}
            return render(request, 'admin_main/admin_manage_coupons.html', context)


@login_required(login_url='admin_login')
def admin_coupons_delete(request):
    if request.user.is_authenticated and request.user.is_superuser:
        coupon_id = request.GET.get('coupon_id')
        coupon = Coupons.objects.get(id=coupon_id)
        coupon.delete()
        messages.info(request, 'Coupon Deleted')
        return redirect('admin_coupons_view')


@login_required(login_url='login')
def user_settings(request):
    return render(request, 'user/user_settings.html')

import json
@login_required(login_url='login')
def confirm_payments(request):
    body = json.loads(request.body)
    print(body)
    payment = Payment(user=request.user,
                      payment_id=body['transID'],
                      order_number=body['orderID'],
                      payment_method=body['payment_method'],
                      # amount_payed = body['amount'],
                      status=body['status'])
    payment.save()
    order = Order.objects.get(order_number=body['orderID'])
    order.payment = payment
    order.save()
    order_items = OrderProduct.objects.filter(order=order)
    for item in order_items:
        item.payment=payment
        item.ordered=True
        item.save()
    data = {
        'order_number': order.order_number,
        'transID': payment.payment_id,
    }
    return JsonResponse(data)



@login_required(login_url='login')
def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')
    try:
        order = Order.objects.get(order_number=order_number)#, is_ordered=True
        order.is_ordered = True
        order.save()
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price

        payment = Payment.objects.get(payment_id=transID)
        cart = CartItems.objects.filter(user=request.user)
        cart.delete()

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
        }
        return render(request, 'store/order_complete.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('index')

@login_required(login_url='login')
def apply_coupon(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        coupon_code = request.POST.get('coupon_code')
        orderno=order_id
        try:
            order = Order.objects.get(id=order_id)
            coupon = Coupons.objects.get(coupon_code=coupon_code)
            if Coupon_Redeemed_Details.objects.filter(user=request.user,
                                                      coupon=coupon, is_redeemed=True).exists():
                messages.error(request, 'This Coupon is already Applied')
                return redirect('payments', orderno=orderno)
            if order.order_total>=float(coupon.MinPurchase) and coupon.ExpDate > date.today():
                order.order_total -= float(coupon.amount)
                order.save()
                crd = Coupon_Redeemed_Details(user=request.user, coupon=coupon, is_redeemed=True)
                crd.save()
                return redirect('payments', orderno=orderno)
            else:
                messages.info(request, "Check Minimum Purchase")
                return redirect('payments', orderno=orderno)
        except:
            messages.info(request, "Sorry Can not Apply this Coupon")
            return redirect('payments', orderno=orderno)


@login_required(login_url='login')
def user_profile_view(request):
    user = User.objects.get(id=request.user.id)
    u = Customer.objects.get(user=user)
    context = {'user':user,'u':u}
    return render(request, 'user/user_profile_view_1.html', context)


@login_required(login_url='login')
def user_profile_edit(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        otp = request.POST.get('otp')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        contact = request.POST.get('contact')
        user = User.objects.get(id=request.user.id)
        try:
            u = Customer.objects.get(user=user)
        except:
            u = Customer(user=user)
            u.save()
        if u.otp == otp:
            user.username=email
            user.email=email
            u.email = email.strip()
        user.first_name=first_name.strip()
        user.last_name=last_name.strip()
        u.contact=contact
        user.save()
        u.save()
        messages.success(request, 'Profile Updated')
        return redirect('user_profile_view')

    user = User.objects.get(id=request.user.id)
    u = Customer.objects.get(user=user)
    edit=True
    context = {'user': user, 'u': u, 'edit':edit}
    return render(request, 'user/user_profile_view_1.html', context)


def verifyEmail(request):
    to_email = request.GET.get('email')
    user = request.user
    otp = str(random.randint(111111, 999999))
    mail_subject = "You are Changing Your Email So Please Verify Using this Email"
    message = render_to_string("mailbody/verify_email.html", {
        'token': f'{otp}',
    })
    customer = Customer.objects.get(user=request.user)
    customer.otp = otp
    customer.save()
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        # messages.success(request, f'Dear {user}, please go to you email {to_email} and check for the OTP \
        #                 Note: Check your spam folder.')
        pass
    else:
        messages.error(request, f'Problem sending email to {to_email}, check if you typed it correctly.')














from . models import ShippingAddress
@login_required(login_url='login')
def user_address_view(request):
    address_list = ShippingAddress.objects.filter(user=request.user)
    context = {'address_list':address_list}
    return render(request, 'user/user_address_view.html', context)

@login_required(login_url='login')
def user_address_add(request):
    if request.method=='POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        address_line_1 = request.POST.get('address_line_1')
        address_line_2 = request.POST.get('address_line_2')
        country = request.POST.get('country')
        state = request.POST.get('state')
        city = request.POST.get('city')
        pincode = request.POST.get('pincode')

        user = User.objects.get(id=request.user.id)

        address = ShippingAddress(user=user,
                                  first_name=first_name.strip(),
                                  last_name=last_name.strip(),
                                  phone=phone,
                                  email=email,
                                  address_line_1=address_line_1.strip(),
                                  address_line_2=address_line_2.strip(),
                                  country=country.strip(),
                                  state=state.strip(),
                                  city=city.strip(),
                                  pincode=pincode)

        if ShippingAddress.objects.filter(user=request.user, is_default=True).exists():
            pass
        else:
            address.is_default = True
            address.save()

        address.save()
        messages.success(request, 'Address Added')
        return redirect('user_address_view')
    # else:
    #     return render(request, 'user/user_address_add.html')


@login_required(login_url='login')
def user_address_edit(request):
    if request.method=='POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        address_line_1 = request.POST.get('address_line_1')
        address_line_2 = request.POST.get('address_line_2')
        country = request.POST.get('country')
        state = request.POST.get('state')
        city = request.POST.get('city')
        pincode = request.POST.get('pincode')
        address_id = request.POST.get('address_id')
        address = ShippingAddress.objects.get(id=address_id)

        # user = user,
        address.first_name = first_name.strip()
        address.last_name = last_name.strip()
        address.phone = phone
        address.email = email.strip()
        address.address_line_1 = address_line_1.strip()
        address.address_line_2 = address_line_2.strip()
        address.country = country.strip()
        address.state = state.strip()
        address.city = city.strip()
        address.pincode = pincode
        address.save()
        address_list = ShippingAddress.objects.filter(user=request.user)
        context = {'address_list': address_list}
        return render(request, 'user/user_address_view.html', context)
        # context = {'address': address}
        # return render(request, 'user/user_address_edit.html', context)
    else:
        edit = True
        address_id = request.GET.get('address_id')
        address = ShippingAddress.objects.get(id=address_id)
        address_list = ShippingAddress.objects.filter(user=request.user)
        context = {'address_list': address_list,'address':address,'edit':edit}
        return render(request, 'user/user_address_view.html', context)


@login_required(login_url='login')
def user_address_delete(request):
    address_id = request.GET.get('address_id')
    address = ShippingAddress.objects.get(id=address_id)
    address.delete()
    messages.success(request, 'Address Deleted')
    return redirect('user_address_view')


def _wishlist_id(request):
    guest = request.session.session_key
    if not guest:
        guest = request.session.create()
    return guest


from . models import WishList,Guest
def add_item_to_wish_list(request, product_id):
    if request.user.is_authenticated:
        product = Products.objects.get(uid=product_id)
        wishlist_item = WishList.objects.filter(product=product, user=request.user)

        if wishlist_item.exists():  # If the item exists in the wishlist, remove it
            wishlist_item.delete()
        else:  # If the item does not exist in the wishlist, add it
            wish_item = WishList(product=product, user=request.user)
            wish_item.save()

    else:
        return redirect('login')

    previous_page = request.META.get('HTTP_REFERER')
    if previous_page:
        return redirect(previous_page)
    else:
        return redirect('user_wish_list_view')


@login_required(login_url='login')
def remove_item_from_wish_list(request, product_id):
    if request.user.is_authenticated:
        try:
            wish_item = WishList.objects.get(product_id=product_id, user=request.user)
            wish_item.delete()
        except WishList.DoesNotExist:
            pass
    else:
        guest = Guest.objects.get(guest_id=_wishlist_id(request))
        try:
            wish_item = WishList.objects.get(product_id=product_id, guest=guest)
            wish_item.delete()
        except WishList.DoesNotExist:
            pass

    previous_page = request.META.get('HTTP_REFERER')
    if previous_page:
        return redirect(previous_page)
    else:
        return redirect('user_wish_list_view')

@login_required(login_url='login')
def user_wish_list_view(request):
    if request.user.is_authenticated:
        wish_product_list = WishList.objects.all().filter(user=request.user)
        context = {'wish_product_list':wish_product_list}
        return render(request, 'user/user_wish_list_view.html', context)
    else:
        return redirect('login')

@login_required(login_url='login')
def user_view_transaction_details(request):
    transaction_list = Payment.objects.all().filter(user=request.user).exclude(payment_method='cod').order_by('-id')
    context = {'transaction_list':transaction_list}
    return render(request, 'user/user_view_transaction_details.html', context)


@login_required(login_url='login')
def select_address(request,address_id):
    address_l = ShippingAddress.objects.filter(user=request.user)
    if len(address_l) == 1:
        messages.info(request , 'Only One Address is Present, You Can not Unselect this')
        return redirect('checkout')
    address = ShippingAddress.objects.get(id=address_id)
    address.is_default=True
    address.save()
    address_list = ShippingAddress.objects.filter(user=request.user).exclude(id=address_id)
    for ad in address_list:
        ad.is_default = False
        ad.save()
    return redirect('checkout')


from django.http import JsonResponse
def filter_products_by_price(request):
    # if request.method == 'POST':
    minamount = request.GET.get('min_price')
    min_price = int(minamount)
    maxamount = request.GET.get('max_price')
    max_price = int(maxamount)
    if min_price>=0 and max_price<=10000:
        product_list = Products.objects.all().filter(in_store=True, price__gte=min_price, price__lte=max_price)
        category_list = Category.objects.all()
        paginator = Paginator(product_list, 6)
        page = request.GET.get('page')
        paged_product = paginator.get_page(page)
        # wish_list = WishList.objects.filter(user=request.user)
        context = {'product_list': paged_product, 'category_list': category_list,
                   'minprice':min_price, 'maxprice':max_price}
        return render(request, 'store/store.html', context)
    else:
        product_list = Products.objects.all().filter(in_store=True)
        category_list = Category.objects.all()
        paginator = Paginator(product_list, 6)
        page = request.GET.get('page')
        paged_product = paginator.get_page(page)
        messages.info(request, 'Enter Valid Price Range Minimum is 0 and Maximum is 10000')
        context = {'product_list': paged_product, 'category_list': category_list,
                   'minprice': min_price, 'maxprice': max_price}
        return render(request, 'store/store.html', context)
    # else:
    #     minamount = request.POST.get('min_price')
    #     # min_price = int(minamount)
    #     maxamount = request.POST.get('max_price')
    #     # max_price = int(maxamount)
    #     product_list = Products.objects.all().filter(in_store=True)
    #     category_list = Category.objects.all()
    #     paginator = Paginator(product_list, 6)
    #     page = request.GET.get('page')
    #     paged_product = paginator.get_page(page)
    #     # wish_list = WishList.objects.filter(user=request.user)
    #     context = {'product_list': paged_product, 'category_list': category_list}
    #     return render(request, 'store/store.html', context)



from . models import Wallet
@login_required(login_url='login')
def user_wallet_details(request):
    if request.user.is_authenticated:
        user = request.user
        try:
            wallet = Wallet.objects.get(user=user)
        except:
            wallet = Wallet.objects.create(user=user, amount=0)
            wallet.save()
        context = {'wallet':wallet}
        return render(request, 'user/user_wallet_details.html',context)



from . models import Coupon_Redeemed_Details
@login_required(login_url='login')
def redeem_coupon_to_wallet(request):
    if request.user.is_authenticated:
        user = request.user
        if request.method == 'POST':
            coupon_code = request.POST.get('coupon_code')
            try:
                coupon = Coupons.objects.get(coupon_code=coupon_code)
            except Coupons.DoesNotExist:
                messages.error(request, 'This Coupon Code is Invalid')
                return redirect('wallet')

            if coupon.ExpDate < date.today():
                messages.error(request, 'This Coupon has Expired')
                return redirect('wallet')

            if Coupon_Redeemed_Details.objects.filter(user=user, coupon=coupon).exists():
                messages.info(request, 'This Coupon is Already Redeemed')
                return redirect('wallet')

            crd = Coupon_Redeemed_Details(user=user, coupon=coupon, is_redeemed=True)
            crd.save()

            wallet = Wallet.objects.get(user=user)
            wallet.amount += coupon.amount
            wallet.save()

            messages.info(request, 'Coupon Redeemed Successfully')
            return redirect('wallet')

    return redirect('signin')

@login_required(login_url='login')
def pay_from_wallet(request, order_id):
    cur_user = request.user
    order = Order.objects.get(id=order_id)
    try:
        wallet = Wallet.objects.get(user=cur_user)
    except:
        wallet = Wallet.objects.create(user=cur_user, amount=0)
        wallet.save()
    if wallet.amount>order.order_total:
        payment_id = f'uw{order.order_number}{order_id}'
        payment = Payment.objects.create(user=cur_user, order_number=order.order_number,
                                         payment_method='Wallet',payment_id=payment_id,
                                         amount_payed=order.order_total, status='COMPLETED')
        payment.save()
        order.is_ordered = True
        order.payment = payment
        order.save()
        wallet.amount -= order.order_total
        wallet.save()
        cartitems = CartItems.objects.filter(user=cur_user)
        cartitems.delete()
    else:
        messages.warning(request, 'Not Enough Balance in Wallet')
        return redirect('payments', orderno=order_id)
    context = {'order': order}
    return render(request, 'user/cash_on_delivery_confirm.html', context)


from django.db.models import Sum

def sales_summary(request):
    now = timezone.now()
    week_start = now - timedelta(days=now.weekday())
    month_start = now.replace(day=1)
    year_start = now.replace(month=1, day=1)
    total_week = Order.objects.filter(created_at__gte=week_start, created_at__lte=now).aggregate(total=Sum('order_total'))['total']
    total_month = Order.objects.filter(created_at__gte=month_start, created_at__lte=now).aggregate(total=Sum('order_total'))['total']
    total_year = Order.objects.filter(created_at__gte=year_start, created_at__lte=now).aggregate(total=Sum('order_total'))['total']

    low_stock_items = SizeVariant.objects.filter(stock__lt=3)

    context = {
        'total_week': total_week,
        'total_month': total_month,
        'total_year': total_year,
        'low_stock_items':low_stock_items
    }

    return render(request, 'admin_main/sales_summary.html', context)


def low_stock_products(request):
    low_stock_items = SizeVariant.objects.filter(stock__lt=3)
    context = {'low_stock_items': low_stock_items}
    return render(request, 'admin_main/low_stock_products.html', context)

def user_search_products(request):
    # if request.method == 'POST':
    query = request.GET.get('query')
    preprocessed_query = slugify(query).replace(' ', '-')
    product_list = Products.objects.all().filter(Q(in_store=True) & Q(slug__contains=preprocessed_query) | Q(product_name__contains=query) |
                                                 Q(product_description__contains=query))
    category_list = Category.objects.all()
    paginator = Paginator(product_list, 6)
    page = request.GET.get('page')
    paged_product = paginator.get_page(page)
    # wish_list = WishList.objects.filter(user=request.user)
    minprice, maxprice = 0, 10000
    context = {'product_list': paged_product, 'category_list': category_list, 'query':query,
               'minprice':minprice,'maxprice':maxprice}
    return render(request, 'store/store.html', context)
    # else:
        # query = request.GET.get('query')
        # product_list = Products.objects.all().filter(in_store=True).order_by('uid')
        # category_list = Category.objects.all()
        # paginator = Paginator(product_list, 6)
        # page = request.GET.get('page')
        # paged_product = paginator.get_page(page)
        # context = {'product_list': paged_product, 'category_list': category_list}
        # return render(request, 'store/store.html', context)


@login_required(login_url='login')
def user_coupons_view(request):
    current_date = date.today()
    coupons = Coupons.objects.filter(ExpDate__gte=current_date)
    context = {'coupons':coupons}
    return render(request, 'user/user_coupons_view.html', context)


from . models import return_request
@login_required(login_url='login')
def return_request_add(request, item_id=0):
    if request.method == 'POST':
        moreinfo = request.POST.get('moreinfo')
        item_id = request.POST.get('item_id')
        item = OrderProduct.objects.get(id=item_id)
        item.returned = True
        item.save()
        ret_req = return_request(user=request.user,item=item,moreinfo=moreinfo,status="Requested")
        ret_req.save()
        messages.success(request, 'Return Requested')
        return redirect('return_request_view')
    else:
        item = OrderProduct.objects.get(id=item_id)
        context = {'item':item}
        return render(request, 'user/return_request_add.html', context)

@login_required(login_url='login')
def return_request_view(request):
    return_items = return_request.objects.filter(user=request.user).order_by('-timestamp')
    context = {'return_items':return_items}
    return render(request, 'user/return_request_view.html', context)

@login_required(login_url='admin_login')
def admin_return_request_view(request):
    return_items = return_request.objects.all().order_by('-timestamp')
    context = {'return_items': return_items}
    return render(request, 'admin_main/admin_return_request_view.html', context)


from . models import Notification
@login_required(login_url='admin_login')
def admin_return_request_update(request, item_id):
    if request.method == 'POST':
        return_items = return_request.objects.all().order_by('-timestamp')
        item = return_request.objects.get(id=item_id)
        status = request.POST.get(f'status-{item_id}')
        if status is None:
            messages.warning(request, 'No Status is Selected')
            return redirect('admin_return_request_view')
        item.status = status
        item.save()


        if status == 'Accepted':
            try:
                wallet = Wallet.objects.get(user=item.user)
            except:
                wallet = Wallet.objects.create(user=item.user)
                wallet.save()
            wallet.amount += item.item.product_price
            wallet.save()
        if status == 'Accepted':
            notification = Notification(user=item.user, message=f'Your request for Returning Product '
                                                            f'{item.item.product.product_name} has been {status} and the Amount is '
                                                            f'Refunded to Your Wallet')
            notification.save()
        else:
            notification = Notification(user=item.user, message=f'Your request for Returning Product '
                                                                f'{item.item.product.product_name} has been {status}' )
            notification.save()

        messages.info(request, f'Status Updated')
        context = {'return_items': return_items}
        return render(request, 'admin_main/admin_return_request_view.html', context)

@login_required(login_url='login')
def user_notifications_view(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-timestamp')
    for notification in notifications:
        notification.is_read = True
        notification.save()

    context = {'notifications':notifications}
    return render(request, 'user/user_notifications_view.html', context)

@login_required(login_url='login')
def user_notifications_delete(request,not_id):
    nt = Notification.objects.get(id=not_id)
    nt.delete()
    messages.info(request, 'Successfully Deleted')
    return redirect('user_notifications_view')


def handler500(request):
    response = render(request, '500error.html')
    response.status_code = 500
    return response

from django.template import RequestContext
def handler404(request, exception):
    response = render(request,'404.html')
    response.status_code = 404
    return response


from . models import Discounts
def admin_manage_offers(request):
    categories = Category.objects.filter(is_deleted=False)
    discounts = Discounts.objects.all()
    context = {'categories':categories, 'discounts':discounts}
    return render(request, 'admin_main/admin_manage_offers.html', context)



def admin_discount_add(request):
    if request.method == 'POST':
        discount = request.POST.get('discount')
        category_id = request.POST.get('category')
        category = Category.objects.get(uid=category_id)
        if Discounts.objects.filter(category=category).exists():
            messages.warning(request, "There is Already One Discount offer on this product")
            return redirect('admin_manage_offers')
        if len(str(discount)) <=2 or discount == 100:
            discount = int(discount) / 100
            category = Category.objects.get(uid=category_id)
            dis = Discounts(discount=(discount * 100), category=category)
            dis.save()
            product_list = Products.objects.filter(category=category)
            for product in product_list:
                product.discount = discount*100
                product.price = product.rprice - round(product.rprice*discount,2)
                product.save()
                variant_list = SizeVariant.objects.filter(product_id=product)
                for var in variant_list:
                    var.price = round(var.rprice*discount,2)
                    var.save()

            messages.success(request, f'{discount*100}% Discount Added for all Products under {category.category_name}')
        return redirect('admin_manage_offers')


def search_discount(request):
    category_id = request.GET.get('category_id')
    category = Category.objects.filter(uid=category_id,is_deleted=False).first()
    discounts = Discounts.objects.filter(category=category)
    categories = Category.objects.filter(is_deleted=False)
    context = {'categories': categories, 'discounts': discounts}
    return render(request, 'admin_main/admin_manage_offers.html', context)


def admin_discount_delete(request,discount_id):
    discount = Discounts.objects.get(id=discount_id)
    category = discount.category
    product_list = Products.objects.filter(category=category)
    for product in product_list:
        product.discount = 0
        product.price = product.rprice
        product.save()
        variant_list = SizeVariant.objects.filter(product_id=product)
        for var in variant_list:
            var.price = var.rprice
            var.save()
    discount.delete()
    messages.info(request, "Discount Offer Deleted")
    return redirect('admin_manage_offers')


def admin_dashboard(request):
    orders = Order.objects.all().filter(Q(status='Pending')|Q(status='New'))
    order_count = len(orders)

    now = timezone.now()
    week_start = now - timedelta(days=now.weekday())
    month_start = now.replace(day=1)
    year_start = now.replace(month=1, day=1)
    total_week = \
        Order.objects.filter(created_at__gte=week_start, created_at__lte=now).aggregate(total=Sum('order_total'))[
            'total']
    total_month = \
        Order.objects.filter(created_at__gte=month_start, created_at__lte=now).aggregate(total=Sum('order_total'))[
            'total']
    total_year = \
        Order.objects.filter(created_at__gte=year_start, created_at__lte=now).aggregate(total=Sum('order_total'))[
            'total']

    low_stock_items = SizeVariant.objects.filter(stock__lt=3)

    product_quantities = OrderProduct.objects.values('product').annotate(total_quantity=Sum('quantity'))
    sorted_products = product_quantities.order_by('-total_quantity')
    top_3_products = sorted_products[:3]
    product_list = Products.objects.all()

    order_list = Order.objects.all().filter(status='Completed')
    for ord in order_list:
        print("-*-*-*- ", ord.created_at)

    context = {'order_count':order_count,
               'total_week': total_week,
               'total_month': total_month,
               'total_year': total_year,
               'low_stock_items': low_stock_items,
               'top_3_products':top_3_products,
               'product_list': product_list,
               'order_list':order_list
               }
    return render(request, 'admin_main/admin_dashboard.html', context)

from datetime import datetime, time, timedelta

def admin_dashboard_filter(request):
    try:
        from_date = request.GET.get('from-date')
        to_date = request.GET.get('to-date')
        from_date_1 = from_date
        to_date_1 = to_date
        orders = Order.objects.all().filter(Q(status='Pending')|Q(status='New'))
        order_count = len(orders)

        now = timezone.now()
        week_start = now - timedelta(days=now.weekday())
        month_start = now.replace(day=1)
        year_start = now.replace(month=1, day=1)




        total_week = \
            Order.objects.filter(created_at__gte=week_start, created_at__lte=now).aggregate(total=Sum('order_total'))[
                'total']
        total_month = \
            Order.objects.filter(created_at__gte=month_start, created_at__lte=now).aggregate(total=Sum('order_total'))[
                'total']
        total_year = \
            Order.objects.filter(created_at__gte=year_start, created_at__lte=now).aggregate(total=Sum('order_total'))[
                'total']

        low_stock_items = SizeVariant.objects.filter(stock__lt=3)

        product_quantities = OrderProduct.objects.values('product').annotate(total_quantity=Sum('quantity'))
        sorted_products = product_quantities.order_by('-total_quantity')
        top_3_products = sorted_products[:3]
        product_list = Products.objects.all()
        from_date = datetime.strptime(from_date, '%Y-%m-%d')
        # to_date = datetime.strptime(to_date, '%Y-%m-%d')

        from_date = f'{from_date}+00:00'
        to_date = f'{to_date} 23:59:59+00:00'
        if from_date <= to_date:
            order_list = Order.objects.filter(created_at__gte=from_date,created_at__lte=to_date)
            # print(order_list)

        else:
            messages.warning(request, 'Enter Valid Dates')
            return redirect('admin_dashboard')

        context = {'order_count':order_count,
                   'total_week': total_week,
                   'total_month': total_month,
                   'total_year': total_year,
                   'low_stock_items': low_stock_items,
                   'top_3_products':top_3_products,
                   'product_list': product_list,
                   'order_list':order_list,
                   'from_date':from_date_1,
                   'to_date':to_date_1,
                   }
        return render(request, 'admin_main/admin_dashboard.html', context)
    except:
        return redirect('admin_dashboard')