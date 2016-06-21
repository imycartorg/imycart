# -*- coding:utf-8 -*-
from django.shortcuts import render,redirect
from shopcart.models import System_Config,Order
from shopcart.utils import System_Para,handle_uploaded_file
from shopcart.forms import register_form
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
from django.http import HttpResponse
from shopcart.sign import Sign
from shopcart.openplatform.wechat import WechatJSSDKSign
from shopcart.utils import System_Para,my_pagination,get_system_parameters
import json
from django.utils.translation import ugettext as _
from shopcart.functions.product_util_func import get_menu_products
from django.http import Http404
# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger('imycart.shopcart')


# Create your views here.
def view_index(request): 
	ctx = {}
	ctx['system_para'] = get_system_parameters()
	ctx['menu_products'] = get_menu_products()
	ctx['page_name'] = 'Home'
	return render(request,System_Config.get_template_name() + '/index.html',ctx)
	
	
#刷新验证码  
def refresh_captcha(request):  
		to_json_response = dict()  
		to_json_response['status'] = 1  
		to_json_response['new_cptch_key'] = CaptchaStore.generate_key()  
		to_json_response['new_cptch_image'] = captcha_image_url(to_json_response['new_cptch_key'])  
		return HttpResponse(json.dumps(to_json_response), content_type='application/json')

def upload_file(request):
	if request.method == 'POST':
		#form = UploadFileForm(request.POST, request.FILES)
		#if form.is_valid():
		filenames = handle_uploaded_file(request.FILES['file'],'product','52')
		
		if filenames:
			lines = []
			lines.append('<p>大图的文件名：%(image)s</p>' % filenames)
			lines.append('<p>缩略图的文件名：%(thumb)s</p>' % filenames)
			lines.append('<p>大图的URL：%(image_url)s</p>' % filenames)
			lines.append('<p>缩略图的URL：%(thumb_url)s</p>' % filenames)
			return HttpResponse(''.join(lines))
		else:
			return HttpResponse('/faild')
	else:
		raise Http404
