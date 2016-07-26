#coding=utf-8
from django.db import transaction
from django.utils.translation import ugettext as _
import datetime,uuid
from django.core.serializers import serialize,deserialize

import logging
logger = logging.getLogger('imycart.shopcart')

def get_menu_products():
	from shopcart.models import Product
	product_list = Product.objects.filter(is_publish=True)
	return product_list

def get_url(object):
	from shopcart.models import System_Config,Product
	url = System_Config.objects.get(name='base_url').val
	
	if isinstance(object,Product):
		if object.static_file_name == None or object.static_file_name == '':
			return  url + '/product/' + object.id
		else:
			return url + '/' + object.static_file_name
	else:
		return '#'