#coding=utf-8
from django.shortcuts import render,redirect,render_to_response
from django.core.urlresolvers import reverse
from shopcart.models import System_Config,MyUser,Order
from shopcart.utils import System_Para,my_pagination,get_serial_number,get_system_parameters
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse,JsonResponse,Http404
import logging,json
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.translation import ugettext as _
from django.db import transaction

from shopcart.myadmin.admin_utils import get_admin_template_name
# Get an instance of a logger
import logging
logger = logging.getLogger('imycart.shopcart')



@staff_member_required
def view(request):
	ctx = {}
	ctx['system_para'] = get_system_parameters()
	ctx['page_name'] = 'Order List'
	
	return render(request,get_admin_template_name('order_list.html'),ctx)
	
@staff_member_required
def list_view(request):
	ctx = {}
	ctx['system_para'] = get_system_parameters()
	ctx['page_name'] = '订单管理'
	
	ctx['order_list'] = Order.objects.all()
	
	return render(request,get_admin_template_name('order_list_content.html'),ctx)
		
