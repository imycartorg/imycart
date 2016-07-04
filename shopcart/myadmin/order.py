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

def get_page_size():
	try:
		size = System_Config.objects.get(name='admin_order_list_page_size')
	except:
		logger.info('"admin_order_list_page_size" is not setted.Use default value 15.')
		size = 15
	return size

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
	
	if request.method == 'GET':
		order_number = request.GET.get('order_number','')
		ctx['order_number'] = order_number
		user_email = request.GET.get('user_email','')
		ctx['user_email'] = user_email
		
		all = Order.objects.all()
		
		if order_number != '':
			all = all.filter(order_number=order_number)
		
		if user_email != '':
			all = all.filter(user__email=user_email)
		
		
		page_size = get_page_size()
		order_list, page_range = my_pagination(request=request, queryset=all,display_amount=page_size)
		
		ctx['order_list'] = order_list
		ctx['page_range'] = page_range
		ctx['page_size'] = page_size
		ctx['order_count'] = all.count()
		return render(request,get_admin_template_name('order_list_content.html'),ctx)
	else:
		raise Http404
		
		
		
@staff_member_required
def oper(request):	
	if request.method == 'POST':
		oper_ids = request.POST.get('oper-ids','')
		if oper_ids == '':
			raise Http404
		else:
			oper_id_list = oper_ids.split(',')
			for id in oper_id_list:
				try:
					order = Order.objects.get(id=id)
					order.delete()
				except:
					logger.info('Can not find order which id is %s to delete.' % (id))
		return redirect('/admin/order-list/')
	else:
		raise Http404
