#coding=utf-8
from django.shortcuts import render,redirect,render_to_response
from shopcart.models import System_Config
from shopcart.utils import get_system_parameters
from django.core.context_processors import csrf
from shopcart.forms import inquiry_form
from django.http import HttpResponse
from django.utils.translation import ugettext as _
from django.http import Http404
# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger('imycart.shopcart')

# Create your views here.
def add(request):
	ctx = {}
	ctx.update(csrf(request))
	ctx['system_para'] = get_system_parameters()
	ctx['page_name'] = 'Inquiry'

	if request.method == 'POST':
		form = inquiry_form(request.POST) # 获取Post表单数据
		if form.is_valid():# 验证表单
			form.save()
			ctx['result'] = _('Message send successfully.')
			return HttpResponse('OK')
		else:
			ctx['result'] = _('Message send faild.Please try again.')
			return redirect('/contact/show/')

