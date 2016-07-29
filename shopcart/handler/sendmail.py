#coding=utf-8
from shopcart import signals
from django.utils.translation import ugettext as _
import logging
logger = logging.getLogger('imycart.shopcart')

#事件监听函数没法自动运行，需要被装载一下，现在是在主程序的__init__中使用了import功能触发

from django.dispatch import receiver
@receiver(signals.user_registration_success)
def user_registration_success_send_mail(sender, **kwargs):
	logger.info('Enter user_registration_success_send_mail hanlder!')
	email = kwargs['email']
	mail_ctx = {}
	sendmail('user_registration_success_send_mail',email,mail_ctx)
	
@receiver(signals.user_password_modify_applyed)			
def user_password_modify_applyed_send_mail(sender,	**kwargs):
	logger.info('Enter user_password_modify_applyed_send_mail hanlder!')
	email = kwargs['email']
	mail_ctx = {}
	sendmail('user_registration_success_send_mail',email,mail_ctx)

@receiver(signals.user_password_modify_success)
def user_password_modify_success_send_mail(sender,	**kwargs):
	logger.info('Enter user_password_modify_success_send_mail hanlder!')
	email = kwargs['email']
	mail_ctx = {}
	sendmail('user_registration_success_send_mail',email,mail_ctx)

@receiver(signals.product_added_to_cart)		
def product_added_to_cart_send_mail(sender,	**kwargs):
	logger.info('Enter product_added_to_cart_send_mail hanlder!')
	email = kwargs['email']
	mail_ctx = {}
	sendmail('user_registration_success_send_mail',email,mail_ctx)

@receiver(signals.product_added_to_wishlist)	
def product_added_to_wishlist_send_mail(sender,	**kwargs):
	logger.info('Enter product_added_to_wishlist_send_mail hanlder!')
	email = kwargs['email']
	mail_ctx = {}
	sendmail('user_registration_success_send_mail',email,mail_ctx)
			
@receiver(signals.order_was_placed)
def order_was_placed_send_mail(sender,	**kwargs):
	logger.info('Enter order_was_placed_send_mail hanlder!')
	email = kwargs['email']
	mail_ctx = {}
	sendmail('user_registration_success_send_mail',email,mail_ctx)

@receiver(signals.order_was_canceled)
def order_was_canceled_send_mail(sender,	**kwargs):
	logger.info('Enter order_was_canceled_send_mail hanlder!')
	email = kwargs['email']
	mail_ctx = {}
	sendmail('user_registration_success_send_mail',email,mail_ctx)
	
@receiver(signals.order_was_shipped)
def order_was_shipped_send_mail(sender,	**kwargs):
	logger.info('Enter order_was_shipped_send_mail hanlder!')
	email = kwargs['email']
	mail_ctx = {}
	sendmail('user_registration_success_send_mail',email,mail_ctx)
	
@receiver(signals.order_was_complete)
def order_was_complete_send_mail(sender,	**kwargs):
	logger.info('Enter order_was_complete_send_mail hanlder!')
	email = kwargs['email']
	mail_ctx = {}
	sendmail('user_registration_success_send_mail',email,mail_ctx)	

#发送邮件	
def sendmail(type,email,mail_ctx):
	if is_sendmail(type):
		logger.info('Mail [%s] has been sended to [%s].' % (type,email))		
	else:
		logger.info('Mail function is closed.')	
			
#判断是都发送邮件，没有配置则不发送
def is_sendmail(type):
	from shopcart.models import System_Config
	try:
		item = System_Config.objects.get(name=type).val
		if item.lower() == 'true':
			return True
		else:
			return False
	except Exception as err:
		logger.info('System parameter [%s] is not defined. It will not send emails.' % (type))
		return False