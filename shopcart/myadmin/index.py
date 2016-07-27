#coding=utf-8
from django.shortcuts import render,redirect
from shopcart.models import System_Config
from shopcart.utils import get_system_parameters


from django.contrib.admin.views.decorators import staff_member_required
import logging
logger = logging.getLogger('imycart.shopcart')

@staff_member_required
def menu_view(request):
	ctx = {}
	ctx['system_para'] = get_system_parameters()
	
	return render(request,System_Config.get_template_name('admin') + '/menu.html',ctx)
