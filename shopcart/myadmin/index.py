#coding=utf-8
from django.shortcuts import render,redirect
from shopcart.models import System_Config
from shopcart.utils import get_system_parameters

from shopcart.myadmin.admin_utils import get_admin_template_name
from django.contrib.admin.views.decorators import staff_member_required
import logging
logger = logging.getLogger('imycart.shopcart')

@staff_member_required
def menu_view(request):
	ctx = {}
	ctx['system_para'] = get_system_parameters()
	
	return render(request,get_admin_template_name('menu.html'),ctx)
