from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import uuid
# Create your models here.

class Customer(models.Model):
	user = models.ForeignKey(User, blank=True, on_delete=models.CASCADE)
	email = models.CharField(max_length=100)
	contact = models.CharField(max_length=100)
	otp = models.CharField(max_length=6)

	def __str__(self):
		return self.email



class BaseModel(models.Model):
	uid = models.UUIDField(primary_key=True , editable=False , default=uuid.uuid4)
	created_at = models.DateTimeField(auto_now= True)
	updated_at = models.DateTimeField(auto_now_add= True)

	class Meta:
		abstract = True

class Category(BaseModel):
	category_name = models.CharField(max_length=100)
	slug = models.SlugField(unique=True, null=True, blank=True)
	is_deleted = models.BooleanField(default=False)

	def save(self, *args, **kwargs):
		self.slug = slugify(self.category_name)
		super(Category, self).save(*args, **kwargs)

	def __str__(self) -> str:
		return self.category_name



class Products(BaseModel):
	product_name = models.CharField(max_length=100)
	slug = models.SlugField(max_length=100,unique=True, null=True, blank=True)
	category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
	price = models.FloatField()
	discount = models.IntegerField(null=True)
	rprice = models.FloatField()

	product_description = models.TextField()
	image = models.ImageField(upload_to="products")

	is_deleted = models.BooleanField(default=False)
	in_store = models.BooleanField(default=False)
	# color_variant

	def save(self, *args, **kwargs):
		self.slug = slugify(f'{self.product_name}{self.uid}')
		super(Products, self).save(*args, **kwargs)

	def product_count(self):
		no_of_prdts = Products.objects.filter(in_store = True)
		return len(no_of_prdts)


	def __str__(self):
		return self.product_name


class ColorVariant(BaseModel):
	product_id = models.ForeignKey(Products, on_delete=models.CASCADE)
	color = models.CharField(max_length=50)

	def __str__(self):
		return str(self.product_id)


class SizeVariant(BaseModel):
	product_id = models.ForeignKey(Products, on_delete=models.CASCADE)
	Color_id = models.ForeignKey(ColorVariant, on_delete=models.CASCADE)
	size = models.CharField(max_length=50)
	price = models.FloatField()
	rprice = models.FloatField()
	stock = models.IntegerField()


from PIL import Image
class ProductImage(BaseModel):
	product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name="product_images")
	Color_id = models.ForeignKey(ColorVariant, on_delete=models.CASCADE)
	image = models.ImageField(upload_to="products")


class Payment(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	payment_id = models.CharField(max_length=100)
	order_number = models.CharField(max_length=50)
	payment_method = models.CharField(max_length=100)
	amount_payed = models.CharField(max_length=100)
	status = models.CharField(max_length=100)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.payment_method




class Order(models.Model):
	STATUS = (
	('Pending', 'Pending'),
	('New', 'New'),
	('Accepted', 'Accepted'),
	('Completed', 'Completed'),
	('Cancelled', 'Cancelled'),)

	user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
	payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
	order_number = models.CharField(max_length=20)
	first_name = models.CharField(max_length=50)
	last_name = models.CharField(max_length=50)
	phone = models.CharField(max_length=15)
	email = models.EmailField(max_length=50)
	address_line_1 = models.CharField(max_length=50)
	address_line_2 = models.CharField(max_length=50, blank=True)
	country = models.CharField(max_length=50)
	state = models.CharField(max_length=50)
	city= models.CharField(max_length=50)
	pincode = models.CharField(max_length=10)
	order_total = models.FloatField()
	tax = models.FloatField()
	status = models.CharField(max_length=10, choices=STATUS, default='New')
	ip = models.CharField(blank=True, max_length=20)
	is_ordered = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def full_name(self):
		return f'{self.first_name} {self.last_name}'

	def full_address(self):
		return f'{self.address_line_1} {self.address_line_2}'


class OrderProduct(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
	product = models.ForeignKey(Products, on_delete=models.CASCADE, null=True)
	product_price = models.FloatField()
	payment = models.ForeignKey(Payment, on_delete=models.CASCADE, blank=True, null=True)
	order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
	quantity = models.IntegerField(default=0, null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	ordered = models.BooleanField(default=False)
	returned = models.BooleanField(default=False)
	color = models.CharField(max_length=50)
	size = models.CharField(max_length=50)

	# @property
	# def get_total(self):
	# 	total = self.product.price * self.quantity
	# 	return total


class ShippingAddress(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
	first_name = models.CharField(max_length=50)
	last_name = models.CharField(max_length=50)
	phone = models.CharField(max_length=15)
	email = models.EmailField(max_length=50)
	address_line_1 = models.CharField(max_length=50)
	address_line_2 = models.CharField(max_length=50)
	country = models.CharField(max_length=50)
	state = models.CharField(max_length=50)
	city = models.CharField(max_length=50)
	pincode = models.CharField(max_length=10)
	is_default = models.BooleanField(default=False)

	def __str__(self):
		return self.first_name

class uCart(models.Model):
	cart_id = models.CharField(max_length=255, blank=True)
	date_added = models.DateField(auto_now_add=True)

class CartItems(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
	product = models.ForeignKey(Products, on_delete=models.CASCADE)
	product_variant = models.ForeignKey(SizeVariant, on_delete=models.CASCADE)#models.CharField(max_length=50)
	cart = models.ForeignKey(uCart, on_delete=models.CASCADE, null=True)
	quantity = models.IntegerField()
	is_active = models.BooleanField(default=True)

	def sub_total(self):
		return self.quantity * (self.product_variant.price)

	def variant(self):
		try:
			size = SizeVariant.objects.get(uid=self.product_variant)
			color = ColorVariant.objects.get(uid=size.Color_id)
			return size, color
		except:
			pass
		return None,None


from datetime import date
class Coupons(models.Model):
	coupon_code = models.CharField(max_length=10,blank=False,unique=True)
	MinPurchase = models.FloatField(blank=False)
	ExpDate = models.DateField(blank=False)
	amount = models.FloatField(blank=False)
	coupon_type = models.CharField(max_length=50)
	is_deleted = models.BooleanField(default=False)

	def expiry_date(self):
		return str(self.ExpDate)

	def check_expired(self):
		if self.ExpDate < date.today():
			return str('Expired')
		else:
			return str('Active')


	def __str__(self):
		return self.coupon_code


class Guest(models.Model):
	guest_id = models.CharField(max_length=255)
	date_added = models.DateField(auto_now_add=True)


class WishList(models.Model):
	guest = models.ForeignKey(Guest, on_delete=models.CASCADE, null=True)
	user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
	product = models.ForeignKey(Products, on_delete=models.CASCADE)
	date_added = models.DateField(auto_now_add=True)


class Wallet(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
	amount = models.FloatField()
	updated_at = models.DateTimeField(auto_now=True)
	pin = models.CharField(max_length=5)

	def save(self, *args, **kwargs):
		self.amount = round(self.amount, 2)
		super().save(*args, **kwargs)


class Coupon_Redeemed_Details(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
	coupon = models.ForeignKey(Coupons, on_delete=models.CASCADE)
	date_added = models.DateField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	is_redeemed = models.BooleanField(default=False)


class Notification(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	message = models.TextField()
	timestamp = models.DateTimeField(auto_now_add=True)
	is_read = models.BooleanField(default=False)

	def __str__(self):
		return self.message


class return_request(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	# variant_id = models.ForeignKey(SizeVariant, on_delete=models.CASCADE)
	item = models.ForeignKey(OrderProduct, on_delete=models.CASCADE)
	timestamp = models.DateTimeField(auto_now_add=True)
	moreinfo = models.TextField()
	status = models.CharField(max_length=15)

class Discounts(models.Model):
	discount = models.IntegerField()
	category = models.ForeignKey(Category, on_delete=models.CASCADE)

