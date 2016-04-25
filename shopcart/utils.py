#coding=utf-8
from shopcart.models import System_Config,Email,Serial_Number
#引入分页组件
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.mail import EmailMultiAlternatives,get_connection
from django.template import Context,loader
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
from django.db import transaction
from django.utils.translation import ugettext as _
import datetime,uuid
# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger('imycart.shopcart')

def add_captcha(ctx):
	hashkey = CaptchaStore.generate_key()  
	imgage_url = captcha_image_url(hashkey)
	ctx['hashkey'] = hashkey
	ctx['imgage_url'] = imgage_url
	return ctx

def get_serial_number():
	current_date = datetime.datetime.now().strftime('%Y%m%d')
	# 手动让select for update和update语句发生在一个完整的事务里面
	with transaction.atomic():
		# 使用select_for_update来保证并发请求同时只有一个请求在处理，其他的请求
		# 等待锁释放
		try:
			serial_number = Serial_Number.objects.select_for_update().get(work_date=current_date)
		except:
			serial_number = Serial_Number.objects.create(work_date=current_date)
			serial_number.save()
			return format_serial_number(serial_number)
        
		serial_number.serial_number = serial_number.serial_number + 1
		serial_number.save()
		return format_serial_number(serial_number)

def format_serial_number(serial_number):
	suffix = ''
	for i in range(len(str(serial_number.serial_number)),8+1):
		suffix = '0' + suffix
	return serial_number.work_date + suffix + str(serial_number.serial_number)
		
		
def my_pagination(request, queryset, display_amount=10, after_range_num = 5,bevor_range_num = 4):
	#尝试获取每页显示的数量
	try:
		display_amount = int(request.GET.get('page_amount'))
	except:
		pass

    #按参数分页
	paginator = Paginator(queryset, display_amount)
	try:
		#得到request中的page参数
		page =int(request.GET.get('page'))
	except:
		#默认为1
		page = 1
	try:
		#尝试获得分页列表
		objects = paginator.page(page)
	#如果页数不存在
	except EmptyPage:
	#获得最后一页
		objects = paginator.page(paginator.num_pages)
	#如果不是一个整数
	except:
		#获得第一页
		objects = paginator.page(1)
	#根据参数配置导航显示范围
	if page >= after_range_num:
		page_range = paginator.page_range[page-after_range_num:page+bevor_range_num]
	else:
		page_range = paginator.page_range[0:page+bevor_range_num]
	return objects,page_range

class System_Para:
	def __init__(self,_page_title='',_site_name='',_default_welcome_message='',_logo_image='',_base_url='',_contact_address='',_thumb_width=128,_service_email='',_copyright=''):
		self.page_title = _page_title
		self.site_name = _site_name
		self.default_welcome_message = _default_welcome_message
		self.logo_image = _logo_image
		self.base_url = _base_url
		self.contact_address = _contact_address
		self.thumb_width = _thumb_width
		self.service_email = _service_email
		self.copyright = _copyright
	
	@staticmethod	
	def get_default_system_parameters():
		return System_Para(
			_site_name = System_Config.objects.get(name='site_name').val,
			_default_welcome_message = System_Config.objects.get(name='default_welcome_message').val,
			_logo_image = System_Config.objects.get(name='logo_image').val,
			_base_url = System_Config.objects.get(name='base_url').val,
			_contact_address = System_Config.objects.get(name='contact_address').val,
			_thumb_width = System_Config.objects.get(name='thumb_width').val,
			_service_email = System_Config.objects.get(name='service_email').val,
			_copyright = System_Config.objects.get(name='copyright').val
		)
	
	
def my_send_mail(useage,ctx,send_to,title):
	logger.info('准备发送邮件： %s ' % [send_to,])
	try:
		conn = get_connection() # 返回当前使用的邮件后端的实例
		email = Email.objects.get(useage=useage)
		conn.username = email.username# 更改用户名
		conn.password = email.password # 更改密码
		conn.host = email.smtp_host # 设置邮件服务器
		conn.open() # 打开连接
		
		t = loader.get_template('email/' + email.template)
		mail_list = [send_to, ]
		
		EMAIL_HOST_USER = email.email_address
		subject, from_email, to = title, EMAIL_HOST_USER, mail_list
		html_content = t.render(Context(ctx))
		msg = EmailMultiAlternatives(subject, html_content, from_email, to)
		msg.attach_alternative(html_content, "text/html")
		conn.send_messages([msg,]) # 我们用send_messages发送邮件
	except Exception as err:
		logger.error('邮件发送失败：' + str(err))
	finally:
		try:
			if conn:
				logger.info('准备关闭连接：' + str(conn))
				conn.close()# 发送完毕记得关闭连接
		except:
			pass
			
def handle_uploaded_file(f,type='other',id='-1'):
	file_name = ""

	file_names = {}
	
	if not type.endswith('/'):
		type += '/'
	if not id.endswith('/'):
		id += '/'
	
	destination = None
	try:
		path = 'media/' + type + id
		import os
		if not os.path.exists(path):
			os.makedirs(path)
			
		ext = f.name.split('.')[-1]
		logger.debug(str(ext))
		
		#允许上传的类型
		file_allow = ['JPG','JPEG','PNG','GIF']
		if ext.upper() not in file_allow:
			raise Exception('%s File type is not allowed to upload.' % [ext])
		
		random_name = str(uuid.uuid1())
		
		file_name = path + random_name + '.' + ext
		file_thumb_name = path + random_name + '-thumb' + '.' + ext
		
		destination = open(file_name, 'wb+')
		logger.debug('file_name: %s' % file_name)
		for chunk in f.chunks():
			destination.write(chunk)
		destination.close()
		
		result = thumbnail(file_name,file_thumb_name)
		if not result:
			raise Exception('thumbnail failed.')
		else:
			file_names['image'] = file_name
			file_names['thumb'] = file_thumb_name
			file_names['image_url'] = System_Config.get_base_url() + '/' + file_name
			file_names['thumb_url'] = System_Config.get_base_url() + '/' + file_thumb_name
	except Exception as e:
		print(str(e))
	finally:
		if destination:
			destination.close()
	return file_names

def thumbnail(file_name,file_thumb_name):
	#生成缩略图
	from PIL import Image
	try:
		img = Image.open(file_name)
		width = int(System_Config.objects.get(name='thumb_width').val)
		logger.debug('系统参数thumb_width:%s' % [width])
		img.thumbnail((width,width),Image.ANTIALIAS)#对图片进行等比缩放
		img.save(file_thumb_name)#保存图片
		return True		
	except Exception as err:
		logger.error('thumbnail failed:' + str(err))
		return False
	finally:
		if img:
			img.close()
	
class Stack():  
     def __init__(self,size):  
         self.size=size;  
         self.stack=[];  
         self.top=-1;  
     def push(self,ele):  #入栈之前检查栈是否已满  
         if self.isfull():  
             raise Exception("out of range");  
         else:  
             self.stack.append(ele);  
             self.top=self.top+1;  
     def pop(self):             # 出栈之前检查栈是否为空  
         if self.isempty():  
             raise exception("stack is empty");  
         else:  
             self.top=self.top-1;  
             return self.stack.pop();  
       
     def isfull(self):  
         return self.top+1==self.size;  
     def isempty(self):  
         return self.top==-1;