#coding=utf-8
from django.shortcuts import render,redirect
from shopcart.models import Cart,Product,Cart_Products,System_Config
from django.core.context_processors import csrf
from django.http import HttpResponse,JsonResponse
import json,uuid
from django.db import transaction
from shopcart.utils import System_Para
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger('imycart.shopcart')


def add_to_cart(request):
	ctx = {}
	ctx.update(csrf(request))
	result_dict = {}
	
	if request.method =='POST':
		product_to_be_add = json.loads((request.body).decode())		
		
		#cart = None
		if request.user.is_authenticated():
			#找到这个用户的cart
			cart,object = Cart.objects.get_or_create(user=request.user)
			
		else:
			if 'cart_id' in request.COOKIES:
				cart_id = request.COOKIES["cart_id"]
				cart,created = Cart.objects.get_or_create(id=cart_id)
			else:
				cart = Cart.objects.create(user=None)
				
		product = Product.objects.get(id=product_to_be_add['product_id'])
		#如果商品有额外属性，则必须指定额外属性的条目
		
		product_attribute = None
		add_result_flag = True
		min_order_quantity = product.min_order_quantity #最小下单数量
		logger.debug('The min_order_quantity of this product is :%s' % (min_order_quantity))
		try:
			product_attribute_id_to_be_add = int(product_to_be_add['product_attribute_id'])
		except Exception as err:
			logger.error('The product has muti values but not selected.')
			add_result_flag = False
		
		if product.attributes.all() and add_result_flag:
			for pa in product.attributes.all():
				#logger.debug('pa.id %s and product_attribute_id_to_be_add %s' % [str(pa.id),str(product_attribute_id_to_be_add)])
				if pa.id == product_attribute_id_to_be_add:
					product_attribute = pa
					min_order_quantity = pa.min_order_quantity
					logger.debug('The min_order_quantity of this product has been changed to :%s' % (min_order_quantity))
					add_result_flag = True
					break
		
		#判断加入购物车的数量数量否达到了最小下单数量
		quantity = int(product_to_be_add['quantity'])
		if quantity < min_order_quantity:
			result_dict['success'] = False
			result_dict['message'] = _('This product must order more than %s.' % (min_order_quantity))
			add_result_flag = False
		
		if add_result_flag:
			cart_product,create = Cart_Products.objects.get_or_create(cart=cart,product=product,product_attribute=product_attribute)
			cart_product.quantity = cart_product.quantity + quantity
			cart_product.save()
		
			result_dict['success'] = True
			result_dict['message'] = _('Opration successsul.')
		else:
			result_dict['success'] = False
			if not result_dict['message']:
				result_dict['message'] = _('Unknown Exception.')
		
		#为了将cart_id写到cookie里，不得不用response对象，要不然可以简单的使用上面这句
		response = HttpResponse()
		response['Content-Type'] = "text/javascript"
		response.write(json.dumps(result_dict))
		response.set_cookie('cart_id',cart.id)
		return response

def ajax_modify_cart(request):
	cart = json.loads((request.body).decode())
	#cart_to_find = {'cart_id':2}
	result_dict = {}
	result_dict['success'] = False
	result_dict['message'] = 'Parameter Error.'
	result_dict['cart_product_total'] = 0.00
	result_dict['sub_total'] = 0.00
	
	if 'method' in cart:
		if cart['method'] == 'clear':
			#这种情况下，cart_id代表购物车cart本身的id，不是购物车中每一条记录的id
			parent_cart = Cart.objects.get(id=cart['cart_id'])
			for cp in parent_cart.cart_products.all():
				cp.delete()
				
			result_dict['sub_total'] = parent_cart.get_sub_total()
			result_dict['success'] = True
			result_dict['message'] = _('Opration successful.')
			return JsonResponse(result_dict)
		
		#如果不是clear，则表明cart_id代表的是购物车中每一笔记录的id
		try:
			cart_exist = Cart_Products.objects.get(id=cart['cart_id'])
		except:
			#记录没找到，则直接报错
			logger.info('cart %s not found.' % [cart['cart_id']])
			return JsonResponse(result_dict)
	
		if cart['method'] == 'add':
			cart_exist.quantity = cart_exist.quantity + int(cart['quantity'])
			cart_exist.save()
			result_dict['cart_product_total'] = cart_exist.get_total()
			result_dict['sub_total'] = cart_exist.cart.get_sub_total()
		elif cart['method'] == 'sub':
			quantity = cart_exist.quantity - int(cart['quantity'])
			#不可减到1个以下
			if cart_exist.quantity <= 0:
				cart_exist.quantity = 1			
			if not set_cart_product_quantity(quantity,cart_exist,result_dict):
				return JsonResponse(result_dict)

		elif cart['method'] == 'del':
			parent_cart = cart_exist.cart
			cart_exist.delete()
			result_dict['sub_total'] = parent_cart.get_sub_total()			
		elif cart['method'] == 'set':
			quantity = int(cart['quantity'])
			if not set_cart_product_quantity(quantity,cart_exist,result_dict):
				return JsonResponse(result_dict)
		else:
			return JsonResponse(result_dict)
			
		#如果上面没报错，则成功
		result_dict['success'] = True
		result_dict['message'] = _('Opration successful.')
	
	return JsonResponse(result_dict)

def set_cart_product_quantity(quantity,cart_exist,result_dict):
	logger.debug('at least:' + str(cart_exist.product_attribute.min_order_quantity))
	if quantity >= cart_exist.product_attribute.min_order_quantity:
		cart_exist.quantity = quantity
		cart_exist.save()
		result_dict['cart_product_total'] = cart_exist.get_total()
		result_dict['sub_total'] = cart_exist.cart.get_sub_total()
		return True
	else:
		result_dict['message'] = 'The product must order more than %s' % (cart_exist.product_attribute.min_order_quantity)
		result_dict['origin'] = cart_exist.quantity
		return False

def view_cart(request):
	ctx = {}
	ctx['system_para'] = System_Para.get_default_system_parameters()
	if request.method =='GET':
		if 'cart_id' in request.COOKIES:
			cart_id = request.COOKIES["cart_id"]
			cart,created = Cart.objects.get_or_create(id=cart_id)
		else:
			if request.user.is_authenticated():
				cart,object = Cart.objects.get_or_create(user=request.user)
			else:
				cart = Cart.objects.create(user=None)
		ctx['cart'] = cart
		response = render(request,System_Config.get_template_name() + '/cart_detail.html',ctx)
		response.set_cookie('cart_id',cart.id)
		return response

@login_required()
def check_out(request): 
	ctx = {}
	ctx['system_para'] = System_Para.get_default_system_parameters()
	
	if request.method == 'POST':
		#得到cart_product_id
		cart_product_id_list = request.POST.getlist('cart_product_id',[])
		cart_product_list = Cart_Products.objects.filter(id__in=cart_product_id_list)
		
		sub_total = 0.00
		for cp in cart_product_list:
			sub_total = sub_total + cp.get_total()
		
		#TODO:添加优惠
		discount = 0.00
		#TODO:添加邮费
		shipping = 0.00
		ctx['product_list'] = cart_product_list
		ctx['sub_total'] =  sub_total + shipping - discount
		ctx['shipping'] = shipping
		ctx['discount'] = discount
		ctx['total'] = sub_total + shipping - discount
		
		#找出用户的地址簿
		myuser = request.user
		ctx['default_address_id'] = '-1'
		try:
			ctx['default_address_id'] = myuser.addresses.filter(is_default=True)[0].id
		except:
			pass
		return render(request,System_Config.get_template_name() + '/check_out.html',ctx)
	else:
		return redirect(reverse('cart_view_cart'))