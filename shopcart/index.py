# -*- coding:utf-8 -*-
from django.shortcuts import render,redirect
from shopcart.models import System_Config,Order
from shopcart.utils import System_Para,handle_uploaded_file
from shopcart.forms import register_form
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
from django.http import HttpResponse
from shopcart.openplatform import signature
import json
from django.utils.translation import ugettext as _
from django.http import Http404
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
	#ctx['i18n_text'] = _('Welcome to %(site_name)s.') % {'site_name':'imycart.com 小伙伴的购物车'}
	ctx['i18n_text'] = _('You are resetting you password in %(sitename)s .') % {'sitename':System_Config.objects.get(name='site_name').val}
	ctx['i18n_text_test'] = _('Today is %(sitename)s.') % {'sitename': 9}
	ctx['i18n_text_near_example'] = _('Today is %(month)s.') % {'month': 9}
	ctx['i18n_text_example'] = _('Today is %(month)s %(day)s.') % {'month': 9, 'day': 6}
	ctx['value'] = 2980.0
	ctx['show_const'] = Order.ORDER_STATUS_PAYED_UNCONFIRMED
	logger.info('i18n_text:' + ctx['i18n_text'])
	
	
	#测试下微信的分享功能
	token = System_Config.objects.get(name='weixin_token').val
	nonce = 'jDZLZ9xJl277grT1'
	import time
	timestamp = str(int(time.time()))
	signature_str = signature(nonce,timestamp,token)
	ctx['token'] = token
	ctx['nonce'] = nonce
	ctx['timestamp'] = timestamp
	ctx['signature'] = signature_str
	
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
