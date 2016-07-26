# -*- coding:utf-8 -*-
from django.shortcuts import render,redirect
from django.http import HttpResponse,Http404
from django.http import JsonResponse,QueryDict
from shopcart.models import System_Config,Product,Product_Images,Category,MyUser,Email,Reset_Password,Address,Product_Attribute,Attribute_Group,Attribute,Article,Express,ExpressType
from shopcart.utils import my_send_mail,get_serial_number
from django.db import transaction
from django.utils.translation import ugettext as _
import datetime
import requests
from shopcart.utils import get_system_parameters
from shopcart.functions.product_util_func import get_menu_products
# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger('imycart.shopcart')


def contact_page(request):
	ctx = {}
	ctx['system_para'] = get_system_parameters()
	ctx['menu_products'] = get_menu_products()
	ctx['page_name'] = 'Contact us'
	
	return render(request,System_Config.get_template_name() + '/contact.html',ctx)

def url_dispatch(request,url):
	logger.debug('Url to dispatch:' + url)
	
	from shopcart.models import Product,Category,Article
	#优先级 1 ：解析商品路径
	try:
		product = Product.objects.get(static_file_name=url)
		#mvc解析
		from shopcart.product import detail
		return detail(request,product.id)
		
		#301跳转模式
		#return redirect('/product/'+str(product.id))
	except Exception as err:
		logger.error('Can not find url [%s] in products.' % (url))
	
	
	#优先级 2 ：解析分类路径
	#暂未实现
	
	#优先级 3 ：解析文章路径
	try:
		article = Article.objects.get(static_file_name=url)
		from shopcart.article import detail
		return detail(request,article.id)
	except Exception as err:
		logger.error('Can not find url [%s] in artilces.' % (url))
		
	raise Http404
	
	
@transaction.atomic()
def init_database(request):
	try:
		flag = System_Config.objects.get(name='inited_flag').val
		logger.info('Init flag has been setted.')
		return HttpResponse('数据已经初始化，不可重复执行。')
	except:
		System_Config.objects.create(name='inited_flag',val='inited')
		pass
	
	cat = Category(code='whole',name='所有品类')
	cat.save()
	
	express_type_fastest = ExpressType.objects.create(name='Fastest',price_fixed=10.00,price_per_kilogram=0)
	express_type_faster = ExpressType.objects.create(name='Faster',price_fixed=8.00,price_per_kilogram=0)
	express_type_normal = ExpressType.objects.create(name='Normal',price_fixed=6.00,price_per_kilogram=0)
	
	express = Express.objects.create(name='Fedx',price_fixed=0.00,price_per_kilogram=0)
	express.express_types.add(express_type_fastest)
	express.express_types.add(express_type_faster)
	express.save()
	
	express = Express.objects.create(name='DHL',price_fixed=0.00,price_per_kilogram=0)
	express.express_types.add(express_type_faster)
	express.save()
	
	express = Express.objects.create(name='EMS',price_fixed=0.00,price_per_kilogram=0)
	express.express_types.add(express_type_normal)
	express.save()
	
	sys_con = System_Config.objects.create(name='template_name',val='cassie')
	sys_con = System_Config.objects.create(name='site_name',val='iMyCart 小伙伴们的购物车')
	sys_con = System_Config.objects.create(name='default_welcome_message',val='Hi，欢迎来iMyCart')
	sys_con = System_Config.objects.create(name='logo_image',val='http://www.imycart.com/images/logo.png')
	sys_con = System_Config.objects.create(name='base_url',val='http://aws.imycart.com')
	sys_con = System_Config.objects.create(name='paypal_account',val='demo@imycart.com')
	sys_con = System_Config.objects.create(name='default_currency',val='USD')
	sys_con = System_Config.objects.create(name='paypal_env',val='sandbox')
	
	sys_con = System_Config.objects.create(name='copyright',val='Copyright © cassiecomb.com All Rights Reserved. Designed by iMyCart')
	sys_con = System_Config.objects.create(name='service_email',val='info@cassiecomb.com')
	sys_con = System_Config.objects.create(name='contact_address',val='4578 MARMORA ROAD,GLASGOW D04 89 GR')
	sys_con = System_Config.objects.create(name='thumb_width',val='128')
	
	sys_con = System_Config.objects.create(name='hot_line',val='(+86)186 18 18 18')
	sys_con = System_Config.objects.create(name='office_phone',val='(+86)86688668')
	
	sys_con = System_Config.objects.create(name='workday',val='Mon - Sun / 9:00AM - 8:00PM(BeiJing Time)')
	
	sys_con = System_Config.objects.create(name='product_page_size',val=12)
	sys_con = System_Config.objects.create(name='common_user_address_limit',val=4)
	sys_con = System_Config.objects.create(name='order_list_page_size',val=10)
	sys_con = System_Config.objects.create(name='blog_list_page_size',val=12)

	
	ag_Color = Attribute_Group.objects.create(name='Color',group_type='image',code='Color')
	
	ab_Color_RED =  Attribute.objects.create(name='RED',group=ag_Color,position=0,thumb='http://aws.imycart.com/media/attribute/Color/RED.jpg')
	ab_Color_GREEN =  Attribute.objects.create(name='GREEN',group=ag_Color,position=1,thumb='http://aws.imycart.com/media/attribute/Color/GREEN.jpg')
	ab_Color_BLUE =  Attribute.objects.create(name='BLUE',group=ag_Color,position=2,thumb='http://aws.imycart.com/media/attribute/Color/BLUE.jpg')
	
	
	product_brush = Product(item_number='BRUSH001',name='Top-quality no tangle 360° hair brush ball',quantity=500,market_price=14.99,price=9.99,description='',short_desc='Contrary to popular belief, Lorem Ipsum is not simply random text. It has roots in a piece of classical Latin literature from 45 BC, making it over 2000 years old.',static_file_name='',is_publish=True)
	product_brush.description = '<p>This kind hair brush can do many different workmanship, so you can choose what you like. Because its personalized shape and design make it become the most popular hair brush in the world, especially in North America. It is the hottest seller and many surprises wait for you.</p><div>1. Portable, for woman can put it in bag.</div><div>2. The different length of tooth can massage the different surface of hair so can protect your hair from damage and loss.</div><div>3. Can do many cover designs, like figure, scenery and animation.</div><div>4. The unique cone shaped plastic bristles work to separate the hair sideways instead of down, gently unraveling even the toughest tangles</div><div>5. Great for Extensions</div><div>6. Our brush also encourages hair growth. The bristles massage the scalp, which stimulates the capillaries, increasing blood circulation, oxygen and nutrients to the hair follicle.</div>'
	product_brush.save()
	product_brush.thumb = 'http://aws.imycart.com/media/product/18/003fee96-1d8b-11e6-b3b0-0ab91c1e4bd1-thumb.jpg'
	product_brush.image = 'http://aws.imycart.com/media/product/18/003fee96-1d8b-11e6-b3b0-0ab91c1e4bd1.jpg'
	product_brush.save()
	
	image_red = Product_Images()
	image_red.product = product_brush
	image_red.thumb = 'http://aws.imycart.com/media/product/18/fce1b180-1d8a-11e6-b3b0-0ab91c1e4bd1-thumb.jpg'
	image_red.image = 'http://aws.imycart.com/media/product/18/fce1b180-1d8a-11e6-b3b0-0ab91c1e4bd1.jpg'
	image_red.save()
	
	image_black = Product_Images()
	image_black.product = product_brush
	image_black.thumb = 'http://aws.imycart.com/media/product/18/003fee96-1d8b-11e6-b3b0-0ab91c1e4bd1-thumb.jpg'
	image_black.image = 'http://aws.imycart.com/media/product/18/003fee96-1d8b-11e6-b3b0-0ab91c1e4bd1.jpg'
	image_black.save()
	
	pa_red = Product_Attribute.objects.create(product=product_brush,sub_item_number=1,quantity=500,price_adjusment=-0.99,image=image_red)
	pa_red.attribute.add(ab_Color_RED)
	pa_red.name = 'RED'
	pa_red.min_order_quantity = 10
	pa_red.save()
	
	pa_green = Product_Attribute.objects.create(product=product_brush,sub_item_number=2,quantity=420,price_adjusment=1.99,image=image_black)
	pa_green.attribute.add(ab_Color_GREEN)
	pa_green.name = 'GREEN'
	pa_green.min_order_quantity = 0
	pa_green.save()
	
	pa_blue = Product_Attribute.objects.create(product=product_brush,sub_item_number=3,quantity=360,price_adjusment=0,image=image_red)
	pa_blue.attribute.add(ab_Color_BLUE)
	pa_blue.name = 'BLUE'
	pa_blue.min_order_quantity = 5
	pa_blue.save()	
	

	myuser = MyUser.objects.create_superuser(email='super@imycart.com',password='imycart',username='Super',gender='1')
	myuser.is_superuser = True
	myuser.save()
	
	email = Email.objects.create(useage='register',email_address='service@imycart.com',smtp_host='smtp.mxhichina.com',username='service@imycart.com',password='Imycart2015',template='register_email.html')
	email = Email.objects.create(useage='reset_password',email_address='service@imycart.com',smtp_host='smtp.mxhichina.com',username='service@imycart.com',password='Imycart2015',template='reset_password.html')
	
	return HttpResponse('成功.尝试产生几个流水号：' + get_serial_number() + "||" + get_serial_number() + "||" + get_serial_number())