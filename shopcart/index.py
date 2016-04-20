# -*- coding:utf-8 -*-
from django.shortcuts import render,redirect
from shopcart.models import System_Config
from shopcart.utils import System_Para
from shopcart.forms import register_form
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
from django.http import HttpResponse
import json
from django.utils.translation import ugettext as _
# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger('imycart.shopcart')


# Create your views here.
def view_index(request): 
	logger.info('开始展示首页')
	hashkey = CaptchaStore.generate_key()  
	imgage_url = captcha_image_url(hashkey)
	ctx = {}
	ctx['system_para'] = System_Para.get_default_system_parameters()
	ctx['hashkey'] = hashkey
	ctx['imgage_url'] = imgage_url
	ctx['i18n_text'] = _('Welcome to imycart.com')
	logger.info('i18n_text:' + ctx['i18n_text'])
	return render(request,System_Config.get_template_name() + '/index.html',ctx)
	
	
#刷新验证码  
def refresh_captcha(request):  
		to_json_response = dict()  
		to_json_response['status'] = 1  
		to_json_response['new_cptch_key'] = CaptchaStore.generate_key()  
		to_json_response['new_cptch_image'] = captcha_image_url(to_json_response['new_cptch_key'])  
		return HttpResponse(json.dumps(to_json_response), content_type='application/json')

"""
def view_index(request):
	return redirect('/product/')
	#ctx = {}
	#ctx['system_para'] = System_Para.get_default_system_parameters()
	#ctx['form'] = register_form()
	#return render(request,System_Config.get_template_name() + '/index.html',ctx)
"""
