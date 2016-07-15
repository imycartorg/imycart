#coding=utf-8
from django.shortcuts import render
from django.template.loader import render_to_string
from shopcart.models import System_Config,Promotion
import json
from django.http import JsonResponse,Http404,HttpResponse
from django.utils.translation import ugettext as _
import logging
logger = logging.getLogger('imycart.shopcart')

# Create your views here.
def calculate(request):
	if request.method == 'POST':
		code = request.GET.get('code','')
		try:
			promotion = Promotion.objects.get(code=code)
		except:
			raise Http404
		
		import importlib
		#装载优惠方法实现类
		module = 'shopcart.promotion_impl.%s' % (promotion.impl_class)
		logger.info('The promotion impl class is [%s] ' %(module))
		try:
			promotion_impl = importlib.import_module(module)
		except Exception as err:
			logger.error('Can not load module:[%s]' % (module))
			raise Http404
		
		
		
		return JsonResponse(promotion_impl.calculate(request,promotion)) 
	
		
