from store.models import Category,uCart,CartItems
from .views import _cart_id, _wishlist_id

def category_list_processor(request):
    category_list = Category.objects.all()
    return {'category_list': category_list}

def cart_counter(request):
    cart_count = 0
    try:
        if request.user.is_authenticated:
            cart_items = CartItems.objects.all().filter(user=request.user)
        else:
            cart = uCart.objects.filter(cart_id=_cart_id(request))
            cart_items = CartItems.objects.all().filter(cart=cart[:1])
        for cart_item in cart_items:
            cart_count += cart_item.quantity
    except uCart.DoesNotExist:
        cart_count=0
    return dict(cart_count=cart_count)


from . models import Guest, WishList

def wish_counter(request):
    if request.user.is_authenticated:
        wish_items = WishList.objects.filter(user=request.user)
    else:
        guest = Guest.objects.filter(guest_id=_wishlist_id(request)).first()
        if guest:
            wish_items = WishList.objects.filter(guest=guest)
        else:
            wish_items = []

    wish_count = wish_items.count() if wish_items else 0

    return {'wish_count': wish_count}


from . models import Notification
def notification_counter(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user=request.user,is_read=False)
        noti_count = notifications.count() if notifications else 0
        return dict(noti_count=noti_count)
    else:
        return dict(noti_count=0)
