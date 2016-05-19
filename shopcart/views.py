# -*- coding:utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse,QueryDict
from shopcart.models import System_Config,Product,Product_Images,Category,MyUser,Email,Reset_Password,Address,Product_Attribute,Attribute_Group,Attribute,Article,Express
from shopcart.utils import my_send_mail,get_serial_number
from django.db import transaction
from django.utils.translation import ugettext as _
import datetime
import requests
# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger('imycart.shopcart')


def read_file(path):
	file_content = None
	with open(path,'rb') as desc_file:
		file_content = desc_file.read().decode('utf-8')
	return file_content

def add_product_manual(request):
	logger.info('开始人工添加商品')
	cat = Category.objects.get(code='twopart')
	
	#读取描述文件
	description = ''
	with open('e:\python\description.txt','rb') as desc_file:
		description = desc_file.read().decode('utf-8')
		#for each_line in desc_file:
		#	description = description + each_line
		
	add_product(item_number='SN2016',name='Apple iPhone 10s Plus 手机',quantity = 999,price = 388.00,market_price = 7999.00,description=description,categorys=[cat,],short_desc='苹果手机就是好')
	product = Product.objects.order_by('create_time').reverse()[0]
	return HttpResponse('成功:/product/' + str(product.id))

def add_product(item_number,name,quantity,price,market_price,description,categorys,short_desc,is_need_attr=True,is_discard_some_attr=False,is_need_gender_attr=False,static_file_name=None):
	product = Product(item_number=item_number,name=name,quantity=quantity,market_price=market_price,price=price,description=description,short_desc=short_desc,static_file_name=static_file_name)
	product.thumb = 'http://120.24.92.125/upload/s1.jpg'
	product.image = 'http://120.24.92.125/upload/b1.jpg'
	product.save()
	
	product.categorys = categorys
	product.save()
	
	image1 = Product_Images()
	image1.product = product
	image1.thumb = 'http://120.24.92.125/upload/s1.jpg'
	image1.image = 'http://120.24.92.125/upload/b1.jpg'
	image1.save()
	
	image2 = Product_Images()
	image2.product = product
	image2.thumb = 'http://120.24.92.125/upload/s2.jpg'
	image2.image = 'http://120.24.92.125/upload/b2.jpg'
	image2.save()
	
	image3 = Product_Images()
	image3.product = product
	image3.thumb = 'http://120.24.92.125/upload/s3.jpg'
	image3.image = 'http://120.24.92.125/upload/b3.jpg'
	image3.save()
	
	size_attr_list = [Attribute.objects.get(name='S'),Attribute.objects.get(name='M'),Attribute.objects.get(name='L')]
	color_attr_list = [Attribute.objects.get(name='White'),Attribute.objects.get(name='Black')]
	gender_attr_list = [Attribute.objects.get(name='Male'),Attribute.objects.get(name='Female')]
	
	pa_list = []
	index = 1
	
	if is_need_attr:
		for size_attr in size_attr_list:
			for color_attr in color_attr_list:
				if is_need_gender_attr:
					for gender_attr in gender_attr_list:
						index += 1
						logger.debug('>>>>index:' + str(index))
						if index%2 == 0:
							price_adjusment = index
						else:
							price_adjusment = 0-index
						pa = Product_Attribute.objects.create(product=product,sub_item_number=index,quantity=100+index,price_adjusment=price_adjusment,image=image1)
						pa.attribute.add(size_attr)
						pa.attribute.add(color_attr)
						pa.attribute.add(gender_attr)
						name = size_attr.name + '-' + color_attr.name + '-' + gender_attr.name
						pa.name = name
						pa.save()
				else:
					index += 1
					logger.debug('>>>>index:' + str(index))
					if index%2 == 0:
						price_adjusment = index
					else:
						price_adjusment = 0-index
					pa = Product_Attribute.objects.create(product=product,sub_item_number=index,quantity=100+index,price_adjusment=price_adjusment,image=image1)
					pa.attribute.add(size_attr)
					pa.attribute.add(color_attr)
					pa.name = size_attr.name + '-' + color_attr.name
					pa.save()
	
	return product

def send_mail(request):
	ctx = {}
	ctx['username'] = '倪先生'
	my_send_mail(useage='reset_password',ctx=ctx,send_to='zjuoliver@163.com',title=_('You are resetting you password in %(site_name)s .') % {'site_name':System_Config.objects.get(name='site_name').val})
	return HttpResponse('成功')



@transaction.atomic()
def init_database(request):
	cat = Category(code='whole',name='电脑整机')
	cat.save()
	
	cat_son_laptop = Category(code='laptop',name='笔记本电脑',parent=cat)
	cat_son_laptop.save()
	
	cat_son_desktop = Category(code='desktop',name='桌面电脑',parent=cat)
	cat_son_desktop.save()
	
	cat_grand_son3 = Category(code='superlaptop',name='超级本电脑',parent=cat_son_laptop)
	cat_grand_son3.save()
	
	cat_grand_son4 = Category(code='flat',name='平板电脑',parent=cat_son_laptop)
	cat_grand_son4.save()
	
	cat_grand_son1 = Category(code='allinone',name='一体机电脑',parent=cat_son_desktop)
	cat_grand_son1.save()
	
	cat_grand_son5 = Category(code='twopart',name='分体式电脑',parent=cat_son_desktop)
	cat_grand_son5.save()
	
	cat_grand_son2 = Category(code='minibox',name='迷你盒子电脑',parent=cat_son_desktop)
	cat_grand_son2.save()

	express = Express.objects.create(name='Fedex',price_fixed=5.00,price_per_kilogram=2)
	express = Express.objects.create(name='DHL',price_fixed=6.00,price_per_kilogram=2)
	express = Express.objects.create(name='ChinaPost',price_fixed=8.00,price_per_kilogram=2)
	
	#"""
	sys_con = System_Config.objects.create(name='template_name',val='cassie')
	sys_con = System_Config.objects.create(name='site_name',val='iMyCart 小伙伴们的购物车')
	sys_con = System_Config.objects.create(name='default_welcome_message',val='Hi，欢迎来iMyCart')
	sys_con = System_Config.objects.create(name='logo_image',val='http://www.imycart.com/images/logo.png')
	sys_con = System_Config.objects.create(name='base_url',val='http://nb886.imycart.com')
	sys_con = System_Config.objects.create(name='paypal_account',val='shawnzju@163.com')
	sys_con = System_Config.objects.create(name='default_currency',val='USD')
	
	sys_con = System_Config.objects.create(name='copyright',val='Copyright © cassiecomb.com All Rights Reserved. Designed by iMyCart')
	sys_con = System_Config.objects.create(name='service_email',val='info@cassiecomb.com')
	sys_con = System_Config.objects.create(name='contact_address',val='4578 MARMORA ROAD,GLASGOW D04 89 GR')
	sys_con = System_Config.objects.create(name='thumb_width',val='128')
	
	sys_con = System_Config.objects.create(name='hot_line',val='(+86)186 18 18 18')
	sys_con = System_Config.objects.create(name='office_phone',val='(+86)86688668')
	#"""

	ag_size = Attribute_Group.objects.create(name='尺码',group_type='text',code='size')
	ag_color = Attribute_Group.objects.create(name='颜色',group_type='image',code='color')
	ag_gender = Attribute_Group.objects.create(name='适用性别',group_type='text',code='gender')

	ab_s = Attribute.objects.create(name='S',group=ag_size,position=1)
	ab_m = Attribute.objects.create(name='M',group=ag_size,position=2)
	ab_l = Attribute.objects.create(name='L',group=ag_size,position=3)

	ab_white = Attribute.objects.create(name='White',group=ag_color,position=1,thumb='http://120.24.92.125/upload/s1.jpg')
	#ab_red = Attribute.objects.create(name='Red',group=ag_color,position=2,thumb='http://120.24.92.125/upload/s2.jpg')
	ab_black = Attribute.objects.create(name='Black',group=ag_color,position=3,thumb='http://120.24.92.125/upload/s3.jpg')
	
	ag_male = Attribute.objects.create(name='Male',group=ag_gender,position=1)
	ag_female = Attribute.objects.create(name='Female',group=ag_gender,position=2)
	
	ag_Color = Attribute_Group.objects.create(name='Color',group_type='image',code='Color')
	
	ab_Color_RED =  Attribute.objects.create(name='RED',group=ag_Color,position=0,thumb='http://aws.imycart.com/media/attribute/Color/RED.jpg')
	ab_Color_GREEN =  Attribute.objects.create(name='GREEN',group=ag_Color,position=1,thumb='http://aws.imycart.com/media/attribute/Color/GREEN.jpg')
	ab_Color_BLUE =  Attribute.objects.create(name='BLUE',group=ag_Color,position=2,thumb='http://aws.imycart.com/media/attribute/Color/BLUE.jpg')
	
	
	product_brush = Product(item_number='BRUSH001',name='Top-quality no tangle 360° hair brush ball',quantity=500,market_price=14.99,price=9.99,description='',short_desc='Contrary to popular belief, Lorem Ipsum is not simply random text. It has roots in a piece of classical Latin literature from 45 BC, making it over 2000 years old.',static_file_name='')
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
	pa_red.save()
	
	pa_green = Product_Attribute.objects.create(product=product_brush,sub_item_number=2,quantity=420,price_adjusment=1.99,image=image_black)
	pa_green.attribute.add(ab_Color_GREEN)
	pa_green.name = 'GREEN'
	pa_green.save()
	
	pa_blue = Product_Attribute.objects.create(product=product_brush,sub_item_number=3,quantity=360,price_adjusment=0,image=image_red)
	pa_blue.attribute.add(ab_Color_BLUE)
	pa_blue.name = 'GREEN'
	pa_blue.save()	
	

	categorys1 = [cat_son_desktop,cat_grand_son1,cat_grand_son2]
	categorys2 = [cat_son_laptop,cat_grand_son4]
	p = add_product(item_number='SN1699',name='Apple iPhone 6s Plus (A1699) 64G 玫瑰金色 移动联通电信4G手机',quantity = 999,price = 6388.00,market_price = 7999.00,description='这东西很好',categorys=categorys1,short_desc='苹果手机就是好',is_need_gender_attr=True,static_file_name='apple-iphone-6s-plus-64G.html')
	add_product(item_number='SN1700',name='Samsung S7 Edge 32G 深空灰 4G手机',quantity = 200,price = 4288.00,market_price = 4999.00,description='最新的三星手机',categorys=categorys1,short_desc='三星黑科技，流弊！',is_need_attr=False,static_file_name='samsung-s7-edge-32G.html')
	add_product(item_number='SN1699',name='荣耀7i (ATH-AL00) 3GB+32GB内存版 沙滩金 移动联通电信4G手机',quantity = 999,price = 1999.00,market_price = 2388.00,description='不能同时支持两张CDMA卡；当存在电信卡时，另一张卡只能使用非电信2Ｇ语音业务；如需使用另一张卡的4G/3G业务，需要禁用电信卡，如果两张都是电信卡，只有一张电信卡可以使用。',categorys=categorys2,short_desc='华为手机，国产手机的骄傲。',is_need_attr=False,static_file_name='honor-7i-32G.html')
	add_product(item_number='SN1698',name='奇酷（QiKU） 8681-A01 青春版 移动联通电信4G手机 流光金 双卡双待',quantity = 435,price = 1199.00,market_price = 1599.00,description='这东西很好',categorys=categorys1,short_desc='不知道什么牌子，尼玛。',is_discard_some_attr=True,static_file_name='QiKU-8681-A01.html')
	add_product(item_number='SN1697',name='联想 乐檬 K3 Note（K50-t3s） 16G 珍珠白 移动4G手机 双卡双待',quantity = 387,price = 699.00,market_price = 7999.00,description='这东西很好',categorys=categorys1,short_desc='联想，让世界联通。',is_need_gender_attr=True,static_file_name='lenovo-lemeng-k3-note-16G.html')
	add_product(item_number='SN1696',name='红米Note 2 双网通版 32GB ROM高配 灰色 移动联通双4G手机 双卡双待',quantity = 465,price = 999.00,market_price = 1288.00,description='这东西很好',categorys=categorys1,short_desc='红米Note，屌丝的三星Note。',is_need_attr=False,static_file_name='hongmi-note-32G.html')
	add_product(item_number='SN1695',name='HTC ONE A9 峭壁灰 移动联通双4G手机',quantity = 269,price = 2799.00,market_price = 2799.00,description='这东西很好',categorys=categorys1,short_desc='HTC，你还想重回巅峰吗？',static_file_name='htc-one-a9.html')
	add_product(item_number='SN1694',name='OPPO A31 1GB+16GB内存版 蓝色 电信4G手机 双卡双待',quantity = 378,price = 899.00,market_price = 1088.00,description='这东西很好',categorys=categorys1,short_desc='OPPO 山寨机之王。',is_discard_some_attr=True,static_file_name='oppo-a31-16G.html')
	add_product(item_number='SN1693',name='微软(Microsoft) Lumia 950 XL DS 智享版 (RM-1116) 黑色',quantity = 981,price = 5499.00,market_price = 5999.00,description='这东西很好',categorys=categorys1,short_desc='国企的手机，曾经仅次于华为了。',is_need_attr=False,static_file_name='microsoft-lumia-950-xl-ds.html')
	add_product(item_number='SN1692',name='中兴（ZTE）L680 移动/联通2G 老人手机 深錆色',quantity = 203,price = 268.00,market_price = 300.00,description='这东西很好',categorys=categorys1,short_desc='中兴，何时才能中兴？',static_file_name='zte-l680.html')
	add_product(item_number='SN1691',name='努比亚（nubia）My 布拉格 银白 移动联通4G手机 双卡双待',quantity = 628,price = 1499.00,market_price = 1599.00,description='这东西很好',categorys=categorys1,short_desc='这名字也太特么奇葩了。',static_file_name='nubia-my-blage.html')
	add_product(item_number='SN1690',name='魅族 PRO5 32GB 银黑色 移动联通双4G手机 双卡双待 ',quantity = 139,price = 2799.00,market_price = 3068.00,description='这东西很好',categorys=categorys1,short_desc='魅族，国产机中的战斗机。',static_file_name='meizu-pro-5-32G.html')
	add_product(item_number='SN1689',name='索尼(SONY) E6883 Xperia Z5尊享版 移动联通双4G手机 4K显示屏 镜像银',quantity = 188,price = 5699.00,market_price = 5699.00,description='这东西很好',categorys=categorys1,short_desc='索尼大法，黑科技之王！',static_file_name='sony-e6883-xperia-z5.html')
	add_product(item_number='SN1688',name='摩托罗拉 Moto X Style (XT1570) 32GB 冰山白 移动联通电信4G手机',quantity = 324,price = 3399.00,market_price = 3568.00,description='Moto X Style 热销中！原生流畅系统,5.7英寸2K屏，2100万像素，无接触语音操控！',categorys=categorys1,short_desc='Hello MOTO，曾经的王者。',static_file_name='moto-x-style-xt1570-32G.html')
	add_product(item_number='SN1687',name='摩托罗拉 moto x 极( XT1581) 64GB 玛雅黑 移动联通电信4G手机',quantity = 439,price = 5288.00,market_price = 5688.00,description='实力防碎屏！高通骁龙810处理器！64位真8核！3GB+64GB流畅运行！3760mAH大容量电池！想你所想！【最后一波福利】金箍棒长长长，套餐费降降降！新年猴赛雷，4G套餐享半价！更多惊喜，点击下方【去看看】开抢',categorys=categorys1,short_desc='Hello MOTO，曾经的王者。',static_file_name='moto-x-xt1581-64G.html')
	add_product(item_number='SN1686',name='LG G4（H818）闪耀金 国际版 移动联通双4G手机 双卡双待',quantity = 257,price = 2799.00,market_price = 3298.00,description='5.5英寸2K屏2560×1440，骁龙六核，3G+32G，1600万+800万，大光圈，NFC，OTG，轻敲解码',categorys=categorys1,short_desc='老公牌手机，你好我也好。',static_file_name='lg-g4-h818.html')
	add_product(item_number='SN1685',name='LG V10（LG H968）玫金白 国际版 移动联通双4G手机 双卡双待',quantity = 128,price = 4888.00,market_price = 5020.00,description='坚固：双层玻璃、不锈钢构造、有机硅壳；后1600万，前双500万双摄像头！2K屏，电池可更换。',categorys=categorys1,short_desc='LG，韩国的国民手机，韩国手机的巅峰之作！',static_file_name='lg-v10-h968.html')
	

	myuser = MyUser.objects.create_superuser(email='super@imycart.com',password='imycart',username='Super',gender='1')
	myuser.is_superuser = True
	myuser.save()
	
	myuser = MyUser.objects.create_user(email='shawn@imycart.com',password='imycart',username='Shawn Nee',gender='1')
	address = Address.objects.create(useage='home',first_name='Dong',last_name='Tuo',user=myuser,country='China',province='Zhejiang',city='Hangzhou',district='Xihu',address_line_1="Zheda road, #38,Zhejiang Univercity",zipcode='310000',tel='13800571505')
	address = Address.objects.create(useage='office',first_name='Rick',last_name='Jordan',user=myuser,country='USA',province='DE',city='New Castle',district='Xihu',address_line_1="215 Lisa Dr",address_line_2="YJAPTV",zipcode='19720-9002',tel='19720-9002')
	
	email = Email.objects.create(useage='register',email_address='service@imycart.com',smtp_host='smtp.mxhichina.com',username='service@imycart.com',password='Imycart2015',template='register_email.html')
	email = Email.objects.create(useage='reset_password',email_address='service@imycart.com',smtp_host='smtp.mxhichina.com',username='service@imycart.com',password='Imycart2015',template='reset_password.html')
	reset_password = Reset_Password.objects.create(email='zjuoliver@163.com',validate_code='X3B7',apply_time=datetime.datetime.now(),expirt_time=(datetime.datetime.now() + datetime.timedelta(hours=24)))
	
	article = Article.objects.create(user=myuser,title='About us',folder='about_us',static_file_name='about-us.html',content=read_file('test_data/about-us.txt'),breadcrumbs=read_file('test_data/about-us-breadcrumbs.txt'))
	
	
	
	return HttpResponse('成功.尝试产生几个流水号：' + get_serial_number() + "||" + get_serial_number() + "||" + get_serial_number())