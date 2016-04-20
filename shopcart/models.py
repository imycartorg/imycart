#coding=utf-8
from django.db import models
import uuid
from django.conf import settings
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser,PermissionsMixin
from django.utils.translation import ugettext as _

# Create your models here.
class MyUserManager(BaseUserManager):
    def _create_user(self, username, email, password, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
		
        #if not username:
        #    raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')

        return self._create_user(username, email, password, **extra_fields)

class MyUser(AbstractBaseUser, PermissionsMixin):
	username = models.CharField(max_length=254,unique=True, null=True,db_index=True)
	email = models.EmailField('email address', unique=True, db_index=True, max_length=254)
	mobile_phone = models.CharField(max_length=50,null=True)
	gender = models.CharField(max_length=3,null=True)
	birthday = models.DateField(null=True)
	is_staff = models.BooleanField('staff status', default=False)
	is_active = models.BooleanField('active', default=True)
	create_time = models.DateTimeField(auto_now_add = True,null=True)
	update_time = models.DateTimeField(auto_now = True,null=True)

	USERNAME_FIELD = 'email'

	objects = MyUserManager()

	class Meta:
		db_table = 'myuser'

	def get_full_name(self):
		return self.username

	def get_short_name(self):
		return self.username
		
	def get_human_gender(self):
		if self.gender == '1':
			return 'male'
		elif self.gender == '0':
			return 'female'
		else:
			return 'unknow'


class Address(models.Model):
	useage = models.CharField(max_length=254,default='',null=True)
	is_default = models.BooleanField(default=True)
	first_name = models.CharField(max_length=50,default='',null=True)
	last_name = models.CharField(max_length=50,default='',null=True)
	user = models.ForeignKey(MyUser,null=True,related_name='addresses')
	country = models.CharField(max_length=50,default='',null=True)
	province = models.CharField(max_length=50,default='',null=True)
	city = models.CharField(max_length=50,default='',null=True)
	district = models.CharField(max_length=50,default='',null=True)
	address_line_1 = models.CharField(max_length=100,default='',null=True)
	address_line_2 = models.CharField(max_length=100,default='',null=True)
	zipcode = models.CharField(max_length=50,default='',null=True)
	tel = models.CharField(max_length=50,default='',null=True)
	mobile = models.CharField(max_length=50,default='',null=True)
	sign_building = models.CharField(max_length=50,default='',null=True)
	best_time = models.CharField(max_length=50,default='',null=True)
	create_time = models.DateTimeField(auto_now_add = True)
	update_time = models.DateTimeField(auto_now = True)

class System_Config(models.Model):
	name = models.CharField(max_length = 100)
	val = models.CharField(max_length = 254)
	create_time = models.DateTimeField(auto_now_add = True)
	update_time = models.DateTimeField(auto_now = True)

	@staticmethod
	#获取模板名字
	def get_template_name():
		sys_conf = System_Config.objects.get(name='template_name')
		return sys_conf.val
	
	@staticmethod
	#获取网站根路径
	def get_base_url():
		sys_conf = System_Config.objects.get(name='base_url')
		return sys_conf.val

class Category(models.Model):
	code = models.CharField(max_length = 100,default='',db_index=True)
	name = models.CharField(max_length = 100,default='')
	sort_order = models.CharField(max_length = 100,default='')
	create_time = models.DateTimeField(auto_now_add = True)
	update_time = models.DateTimeField(auto_now = True)
	parent = models.ForeignKey('self',null=True,default=None,related_name='childrens')
	
	def get_parent_stack(self):
		from shopcart.utils import Stack  
		s=Stack(20);
		target = self
		print('self:' + self.code)
		while target is not None:
			print('target:' + target.code)
			s.push(target)
			target = target.parent
		return s
		
	def get_dirs(self):
		from shopcart.utils import Stack 
		s = self.get_parent_stack()
		dir = ''
		while not s.isempty():
			dir = dir + s.pop().code + '/'
		return dir

class Product(models.Model):
	item_number = models.CharField(max_length = 100,default='',db_index=True)
	name = models.CharField(max_length = 100,default='')
	click_count = models.IntegerField(default=0)
	quantity = models.IntegerField(default=0)
	warn_quantity = models.IntegerField(default=0)
	price = models.FloatField()
	market_price = models.FloatField()
	keywords = models.CharField(max_length = 254,default='')
	short_desc = models.CharField(max_length = 254,default='')
	description = models.TextField()
	thumb = models.URLField()
	image = models.URLField()
	is_free_shipping = models.BooleanField(default=False)
	sort_order = models.IntegerField(default=0)
	static_file_name = models.CharField(max_length = 254,null=True)
	categorys = models.ManyToManyField(Category)
	create_time = models.DateTimeField(auto_now_add = True)
	update_time = models.DateTimeField(auto_now = True)

	def get_attributes(self):
		pa_list = self.attributes.all()
		print("pa_list size:" + str(len(pa_list)))
		attribute_list = Attribute.objects.filter(product_attribute__in=pa_list).distinct()
		print("attribute_list size:" + str(len(attribute_list)))
		attribute_group_list = list(set([attr.group for attr in attribute_list]))#用set去重后，再转回list
		print("attribute_group_list size:" + str(len(attribute_group_list)))
		attribute_group_list.sort(key=lambda x:x.position)#利用position字段排序
		
		for ag in attribute_group_list:
			ag.attr_list = [attr for attr in attribute_list if attr.group == ag]
			ag.attr_list.sort(key=lambda x:x.position)
		
		return attribute_group_list
	
		
class Product_Images(models.Model):
	#product_id = models.IntegerField(default=0)
	thumb = models.URLField(null=True)
	image = models.URLField(null=True)
	product = models.ForeignKey(Product,default=None,related_name='images')
	create_time = models.DateTimeField(auto_now_add = True)
	update_time = models.DateTimeField(auto_now = True)

class Attribute_Group(models.Model):
	name = models.CharField(max_length = 100,default='')
	group_type = models.CharField(max_length = 100,default='') #分为text,image两种，一种是前台显示文字，一种是前台显示图片
	position = models.IntegerField(default=0)
	code = models.CharField(max_length = 100,default='') #用于html中用的name属性的
	create_time = models.DateTimeField(auto_now_add = True)
	update_time = models.DateTimeField(auto_now = True)

class Attribute(models.Model):
	group = models.ForeignKey(Attribute_Group,related_name='attributes',null=True)
	name = models.CharField(max_length = 100,default='')
	position = models.IntegerField(default=0)
	thumb = models.URLField(null=True,default=None)
	create_time = models.DateTimeField(auto_now_add = True)
	update_time = models.DateTimeField(auto_now = True)

class Product_Attribute(models.Model):
	product = models.ForeignKey(Product,null=True,related_name='attributes')
	sub_item_number = models.CharField(max_length = 100,default='',db_index=True)
	quantity = models.IntegerField(default=0)
	price_adjusment = models.FloatField()
	image = models.ForeignKey(Product_Images,null=True)
	name = models.CharField(max_length = 254,default='')
	attribute = models.ManyToManyField(Attribute,null=True) 
	create_time = models.DateTimeField(auto_now_add = True)
	update_time = models.DateTimeField(auto_now = True)


class Cart(models.Model):
	user = models.ForeignKey(MyUser,null=True,related_name='mycart')
	create_time = models.DateTimeField(auto_now_add = True)
	update_time = models.DateTimeField(auto_now = True)
	
	def get_sub_total(self):
		total = 0
		for cart_product in self.cart_products.all():
			total = total + cart_product.get_total()
		return total
	
class Cart_Products(models.Model):
	cart = models.ForeignKey(Cart,null=True,related_name='cart_products')
	product = models.ForeignKey(Product,null=True)
	product_attribute = models.ForeignKey(Product_Attribute,null=True)
	quantity = models.IntegerField(default=0)
	create_time = models.DateTimeField(auto_now_add = True)
	update_time = models.DateTimeField(auto_now = True)
	
	def get_total(self):
		return self.quantity * self.get_product_price()
		
	def get_short_product_attr(self):
		attr_list = Attribute.objects.filter(product_attribute=self.product_attribute).distinct()
		ret_str = ''
		for attr in attr_list:
			ret_str = ret_str + ' [' + attr.group.name + ':' + attr.name + ']'
		return ret_str
	
	def get_product_price(self):
		if self.product_attribute is None:
			return self.product.price
		else:
			return self.product_attribute.price_adjusment + self.product.price

	
class Wish(models.Model):
	user = models.ForeignKey(MyUser,null=True,related_name='wishs')
	product = models.ForeignKey(Product,null=True)
	create_time = models.DateTimeField(auto_now_add = True)
	update_time = models.DateTimeField(auto_now = True)

class Email(models.Model):
	useage = models.CharField(max_length = 100,unique=True)
	email_address = models.EmailField(null=True)
	smtp_host = models.CharField(max_length=100)
	username = models.CharField(max_length=100)
	password = models.CharField(max_length=100)
	template = models.CharField(max_length=254)
	create_time = models.DateTimeField(auto_now_add = True)
	update_time = models.DateTimeField(auto_now = True)

class Order(models.Model):
	order_number = models.CharField(max_length = 100,unique=True,db_index=True)
	user = models.ForeignKey(MyUser,null=True,related_name='orders')
	status = models.CharField(max_length = 32,default='0')
	shipping_status = models.CharField(max_length = 100,default='not yet')
	pay_status = models.CharField(max_length = 100,default='wait for payment')
	country = models.CharField(max_length = 100,default='')
	province = models.CharField(max_length = 100,default='')
	city = models.CharField(max_length = 100,default='')
	district = models.CharField(max_length = 100,default='')
	address_line_1 = models.CharField(max_length = 254,default='')
	address_line_2 = models.CharField(max_length = 254,default='')
	zipcode = models.CharField(max_length = 10,default='')
	tel = models.CharField(max_length = 20,default='')
	mobile = models.CharField(max_length = 20,default='')
	email = models.CharField(max_length = 100,default='')
	shipper_name = models.CharField(max_length = 100,default='')
	shpping_no = models.CharField(max_length = 100,default='')
	pay_id = models.CharField(max_length = 100,default='')
	pay_name = models.CharField(max_length = 100,default='')
	products_amount = models.FloatField(default=0.00)
	shipping_fee = models.FloatField(default=0.00)
	discount = models.FloatField(default=0.00)
	order_amount = models.FloatField(default=0.00)
	money_paid = models.FloatField(default=0.00)
	refer = models.CharField(max_length = 10,default='')
	pay_time = models.DateTimeField(null=True)
	shipping_time = models.DateTimeField(null=True)
	to_seller = models.CharField(max_length = 100)
	create_time = models.DateTimeField(auto_now_add = True)
	update_time = models.DateTimeField(auto_now = True)

	def get_human_status(self):
		dict = {'0':'Wait For Payment','10':'Wait For Shipment','20':'Shipping','30':'Complete','40':'Canceled','90':'Payment Error','99':'Closed'}
		return dict[self.status]
	
		
class Order_Products(models.Model):
	product_id = models.IntegerField(default=0)
	product_attribute = models.ForeignKey(Product_Attribute,null=True)
	order = models.ForeignKey(Order,null=True,related_name='order_products')
	name = models.CharField(max_length = 100,default='')
	short_desc = models.CharField(max_length = 254,default='')
	price = models.FloatField()
	thumb = models.URLField()
	image = models.URLField()
	quantity = models.IntegerField(default=0)
	create_time = models.DateTimeField(auto_now_add = True)
	update_time = models.DateTimeField(auto_now = True)
	
	def get_total(self):
		return self.quantity * self.price

class Abnormal_Order(models.Model):
	order = models.ForeignKey(Order,null=True,related_name='abnormal_orders')
	reason = models.CharField(max_length=100,null=True)
	detail = models.TextField()
	create_time = models.DateTimeField(auto_now_add = True)
	update_time = models.DateTimeField(auto_now = True)

class Reset_Password(models.Model):
	email = models.EmailField('email address',max_length=254)
	validate_code = models.CharField(max_length=254)
	is_active = models.BooleanField(default=False)
	apply_time = models.DateTimeField()
	expirt_time = models.DateTimeField()
	create_time = models.DateTimeField(auto_now_add = True)
	update_time = models.DateTimeField(auto_now = True)

class Serial_Number(models.Model):
	work_date = models.CharField(max_length=8,unique=True)
	serial_number = models.IntegerField(default=1)
	create_time = models.DateTimeField(auto_now_add = True)
	update_time = models.DateTimeField(auto_now = True)

class Article(models.Model):
	title = models.CharField(max_length=254,null=True,db_index=True)
	content = models.TextField(null=True)
	user = models.ForeignKey(MyUser,null=True)
	keywords = models.CharField(max_length=254,null=True)
	static_file_name = models.CharField(max_length = 254,null=True)
	folder = models.CharField(max_length = 254,null=True)
	breadcrumbs = models.CharField(max_length = 254,null=True)
	create_time = models.DateTimeField(auto_now_add = True)
	update_time = models.DateTimeField(auto_now = True)

	
	
	
	
	
	