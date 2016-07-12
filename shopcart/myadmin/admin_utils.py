#coding=utf-8
from shopcart.models import System_Config


import logging
logger = logging.getLogger('imycart.shopcart')

def get_admin_template_name(page_name):
	try:
		name = System_Config.objects.get(name='admin_template_name').val
	except:
		name = 'default'
		
	return 'admin/%s/%s' % (name,page_name)

