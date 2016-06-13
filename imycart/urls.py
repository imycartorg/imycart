"""imycart URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import *
from django.conf.urls import include, url
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = patterns("",
	url(r'^$', 'shopcart.index.view_index',name='view_index'),
	url(r'^refresh-captcha$', 'shopcart.index.refresh_captcha',name='refresh_captcha'),	
	url(r'^user/register$', 'shopcart.myuser.register',name='myuser_register'),
	url(r'^user/login/$', 'shopcart.myuser.login',name='myuser_login'),
	url(r'^user/logout/$', 'shopcart.myuser.logout',name='myuser_logout'),
	url(r'^user/forget-password$', 'shopcart.myuser.forget_password',name='myuser_forget_password'),
	url(r'^user/reset-password$', 'shopcart.myuser.reset_password',name='myuser_reset_password'),
	url(r'^user/info/$', 'shopcart.myuser.info',name='myuser_info'),
	url(r'^user/address/opration/(.+)/(.+)/$', 'shopcart.myuser.address',name='myuser_address'),
	url(r'^user/address/opration/(.+)/$', 'shopcart.myuser.address',name='myuser_address'),
	url(r'^user/address/detail/(.+)/$', 'shopcart.myuser.address_detail',name='myuser_address_detail'),
	url(r'^user/address/show/$', 'shopcart.myuser.address_list',name='myuser_address_list'),
	url(r'^validate/user/(.+)/$', 'shopcart.validate.ajax_validate_user',name='validate_ajax_validate_user'),
	url(r'^cart/add$', 'shopcart.cart.add_to_cart',name='cart_add_to_cart'),
	url(r'^cart/modify$', 'shopcart.cart.ajax_modify_cart',name='cart_ajax_modify_cart'),
	url(r'^cart/show/$', 'shopcart.cart.view_cart',name='cart_view_cart'),
	url(r'^cart/check-out$', 'shopcart.cart.check_out',name='cart_check_out'),
	url(r'^cart/re-calculate-price/$', 'shopcart.cart.re_calculate_price',name='re_calculate_price'),
	url(r'^cart/place-order$', 'shopcart.order.place_order',name='order_place_order'),
	url(r'^cart/payment/(\d+)/$', 'shopcart.order.payment',name='order_payment'),
	url(r'^order/show/$', 'shopcart.order.show_order',name='order_show_order'),
	url(r'^order/cancel$', 'shopcart.order.ajax_cancel_order',name='order_ajax_cancel_order'),
	url(r'^wishlist/$', 'shopcart.wishlist.view_wishlist',name='wishlist_view_wishlist'),
	url(r'^wishlist/add$', 'shopcart.wishlist.add_to_wishlist',name='wishlist_add_to_wishlist'),
	url(r'^wishlist/remove$', 'shopcart.wishlist.remove_from_wishlist',name='wishlist_remove_from_wishlist'),
	url(r'^product/(\d+)/$', 'shopcart.product.detail',name='product_detail'),
	url(r'^product/$', 'shopcart.product.view_list',name='product_view_list'),
	url(r'^product/get-product-extra/$', 'shopcart.product.ajax_get_product_info',name='product_ajax_get_product_info'),
	url(r'^product/get-product-description/(\d+)/$', 'shopcart.product.ajax_get_product_description',name='product_ajax_get_product_description'),
	url(r'^article/(\d+)/$', 'shopcart.article.detail',name='article_detail'),
	url(r'^blog/$', 'shopcart.article.view_blog_list',name='article_view_blog_list'),
	url(r'^captcha/', include('captcha.urls')),
	url(r'^ajax_val_captcha/$', 'shopcart.validate.ajax_validate_captcha',name='ajax_validate_captcha'),
	url(r'^paypal/', include('paypal.standard.ipn.urls')),
	url(r'^comments/', include('django_comments.urls')),
	url(r'^file-upload/(.+)/(.+)/$', 'shopcart.admin_views.file_upload',name='admin_file_upload'),
	url(r'^file-delete/(.+)/(.+)/(.+)/$', 'shopcart.admin_views.file_delete',name='admin_file_delete'),
	url(r'^email-list/add/$', 'shopcart.emaillist.add_to_email_list',name='emaillist_add_to_email_list'),
	url(r'^query/product/$', 'shopcart.product.query_product_show',name='product_query_product_show'),

	url('^admin/ckediter/(.+)/(.+)/$', 'shopcart.admin_views.ckediter',name='admin_ckediter'),
	url('^admin/product/make-static/$', 'shopcart.admin_views.product_make_static',name='admin_product_make_static'),
	url('^admin/product/(.+)/(\d+)/$', 'shopcart.admin_views.product_opration',name='admin_product_opration'),
    url(r'^admin/', include(admin.site.urls)),
	url(r'^i18n/', include('django.conf.urls.i18n')),

	#下面是初始化方法
	url(r'^initdb/$', 'shopcart.views.init_database',name='init_database'),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
