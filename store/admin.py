from django.contrib import admin

from .models import *

admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(OrderProduct)
admin.site.register(Payment)
admin.site.register(ShippingAddress)
admin.site.register(Category)
admin.site.register(ColorVariant)
admin.site.register(SizeVariant)
admin.site.register(Products)
admin.site.register(ProductImage)
admin.site.register(uCart)
admin.site.register(CartItems)
admin.site.register(Coupons)
admin.site.register(WishList)
admin.site.register(Guest)
admin.site.register(Coupon_Redeemed_Details)
admin.site.register(Wallet)
admin.site.register(return_request)
admin.site.register(Notification)
