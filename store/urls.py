from django.urls import path,include
from . import views

urlpatterns = [
	path('', views.index, name="index"),
	path('index', views.index, name="index"),
	path('category_list/', views.category_list, name="category_list"),

	path('login/', views.signin, name="login"),
	path('signin/', views.signin_confirmation, name="signin"),
	path('register/', views.register, name="register"),
	path('validateOTP', views.validateOTP, name="validateOTP"),
	path('customer_logout', views.customer_logout, name="customer_logout"),

	path('admin_login/', views.admin_login, name="admin_login"),
	path('admin_home/', views.admin_home, name="admin_home"),
	path('admin_logout/', views.admin_logout, name="admin_logout"),

	path('admin_user_details_view/', views.admin_user_details_view, name="admin_user_details_view"),
	path('admin_block_unblock/', views.admin_block_unblock, name="admin_block_unblock"),

	path('categories/', views.categories, name="categories"),
	path('admin_categories_add/', views.admin_categories_add, name="admin_categories_add"),
	path('admin_categories_edit', views.admin_categories_edit, name="admin_categories_edit"),
	path('admin_categories_delete', views.admin_categories_delete, name="admin_categories_delete"),

	path('admin_products_view', views.admin_products_view, name="admin_products_view"),
	path('admin_product_add', views.admin_product_add, name="admin_product_add"),
	path('admin_product_update', views.admin_product_update, name="admin_product_update"),

	path('admin_product_details_update', views.admin_product_details_update, name="admin_product_details_update"),
	path('product_variants_view', views.product_variants_view, name="product_variants_view"),
	path('product_variants_add', views.product_variants_add, name="product_variants_add"),
	path('product_variant_images/<uuid:color>/', views.product_variant_images, name='product_variant_images'),
	path('product_variant_images_add', views.product_variant_images_add, name="product_variant_images_add"),
	path('product_image_delete/<uuid:image_id>/<uuid:color>/', views.product_image_delete, name='product_image_delete'),
	# path('products/<int:product_id>/', views.product_details, name='product-details'),
	path('delete_product/', views.delete_product, name='delete_product'),

	path('add_remove_product_to_store/<uuid:product_id>/', views.add_remove_product_to_store, name='add_remove_product_to_store'),
	path('product_variants_stock_update/<uuid:size_id>/<uuid:product_id>/', views.product_variants_stock_update,
		 name='product_variants_stock_update'),
	path('product_variants_stock_updates', views.product_variants_stock_updates,
		 name='product_variants_stock_updates'),

	path('variants_stock_update_cancel/<uuid:product_id>/', views.variants_stock_update_cancel,
		 name='variants_stock_update_cancel'),

	path('admin_order_details_view/', views.admin_order_details_view, name='admin_order_details_view'),
	path('admin_order_info_view/<order>/', views.admin_order_info_view, name='admin_order_info_view'),

	path('order_status_update', views.order_status_update, name='order_status_update'),

	path('product_details/<uuid:product_id>/', views.product_details, name='product_details'),
	path('search_product/', views.search_product, name='search_product'),
	path('search_product_price/', views.search_product_price, name='search_product_price'),

	path('size_list', views.size_list, name='size_list'),
	path('show_price', views.show_price, name='show_price'),

	path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
	path('inc_cart_item/<item_id>/', views.inc_cart_item, name='inc_cart_item'),
	path('dec_cart_item/<item_id>/', views.dec_cart_item, name='dec_cart_item'),
	path('remove_from_cart', views.remove_from_cart, name='remove_from_cart'),

	path('cart/', views.cart, name="cart"),
	path('view_store/', views.view_store, name="view_store"),
	path('view_store/<slug:category>/', views.view_store, name="view_store_category"),

	path('user_dashboard/', views.user_dashboard, name="user_dashboard"),
	path('checkout/', views.checkout, name="checkout"),
	path('load_address/', views.load_address, name="load_address"),

	path('place_order/', views.place_order, name="place_order"),
	path('payments/<orderno>', views.payments, name="payments"),
	path('order_complete/', views.order_complete, name="order_complete"),
	path('confirm_payments/', views.confirm_payments, name="confirm_payments"),

	path('order_details/<orderno>/', views.order_details, name="order_details"),
	path('cancel_order/<orderno>/', views.cancel_order, name="cancel_order"),

	path('admin_change_password/', views.admin_change_password, name="admin_change_password"),
	path('get_link/', views.get_link, name="get_link"),

	path('admin_coupons_add/', views.admin_coupons_add, name="admin_coupons_add"),
	path('admin_coupons_view/', views.admin_coupons_view, name="admin_coupons_view"),
	path('admin_coupons_update/', views.admin_coupons_update, name="admin_coupons_update"),
	path('admin_coupons_delete/', views.admin_coupons_delete, name="admin_coupons_delete"),


	path('apply_coupon/', views.apply_coupon, name="apply_coupon"),

	path('user_settings/', views.user_settings, name="user_settings"),
	path('user_profile_view/', views.user_profile_view, name="user_profile_view"),
	path('user_profile_edit/', views.user_profile_edit, name="user_profile_edit"),

	path('user_address_view/', views.user_address_view, name="user_address_view"),
	path('user_address_add/', views.user_address_add, name="user_address_add"),
	path('user_address_edit/', views.user_address_edit, name="user_address_edit"),
	path('user_address_delete/', views.user_address_delete, name="user_address_delete"),
	path('select_address/<int:address_id>/', views.select_address, name="select_address"),

	path('user_order_details/', views.user_order_details, name="user_order_details"),

	path('add_item_to_wish_list/<uuid:product_id>/', views.add_item_to_wish_list, name="add_item_to_wish_list"),
	path('remove_item_from_wish_list/<uuid:product_id>/', views.remove_item_from_wish_list, name="remove_item_from_wish_list"),
	path('user_wish_list_view/', views.user_wish_list_view, name="user_wish_list_view"),

	path('user_view_transaction_details/', views.user_view_transaction_details, name="user_view_transaction_details"),
	path('filter_products_by_price/', views.filter_products_by_price, name='filter_products_by_price'),

	path('cash_on_delivery/<order_id>/', views.cash_on_delivery, name='cash_on_delivery'),

	path('wallet/', views.user_wallet_details, name='wallet'),
	path('redeem_coupon_to_wallet/', views.redeem_coupon_to_wallet, name='redeem_coupon_to_wallet'),
	path('pay_from_wallet/<order_id>/', views.pay_from_wallet, name='pay_from_wallet'),

	path('sales_summary/', views.sales_summary, name='sales_summary'),
	path('low_stock_products/', views.low_stock_products, name='low_stock_products'),

	path('user_search_products/', views.user_search_products, name='user_search_products'),

	path('user_coupons_view/', views.user_coupons_view, name='user_coupons_view'),

	path('return_request_add/<item_id>/', views.return_request_add, name='return_request_add'),
	path('return_request_view/', views.return_request_view, name='return_request_view'),

	path('admin_return_request_view/', views.admin_return_request_view, name='admin_return_request_view'),
	path('admin_return_request_update/<item_id>', views.admin_return_request_update, name='admin_return_request_update'),

	path('user_notifications_view', views.user_notifications_view,
		 name='user_notifications_view'),
	path('user_notifications_delete/<not_id>/', views.user_notifications_delete,
		 name='user_notifications_delete'),

	path('search-user', views.admin_user_details_search,
		 name='admin_user_details_search'),

	path('search-product', views.admin_product_details_search,
		 name='admin_product_details_search'),

	path('search-category', views.admin_category_search,
		 name='admin_category_search'),

	path('product_variants_stock_delete/<uuid:size_id>/<uuid:product_id>/', views.product_variants_stock_delete,
		 name='product_variants_stock_delete'),

	path('verifyEmail', views.verifyEmail, name='verifyEmail'),

	path('admin_manage_offers', views.admin_manage_offers, name='admin_manage_offers'),
	path('admin_discount_add', views.admin_discount_add, name='admin_discount_add'),
	path('search_discount', views.search_discount, name='search_discount'),
	path('admin_discount_delete/<discount_id>/', views.admin_discount_delete, name='admin_discount_delete'),

	path('admin_dashboard', views.admin_dashboard, name='admin_dashboard'),
	path('admin_dashboard_filter', views.admin_dashboard_filter, name='admin_dashboard_filter'),


]


# handler500 = 'store.views.handler500'
# handler400 = 'views.handler400'