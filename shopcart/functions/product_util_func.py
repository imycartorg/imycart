#coding=utf-8
from shopcart.models import Product

from django.db import transaction
from django.utils.translation import ugettext as _
import datetime,uuid
from django.core.serializers import serialize,deserialize

import logging
logger = logging.getLogger('imycart.shopcart')

def get_menu_products():
	product_list = Product.objects.all()
	return product_list


		 