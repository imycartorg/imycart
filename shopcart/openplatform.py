# -*- coding: UTF-8 –*-
# Create your views here.
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import logging
logger = logging.getLogger('imycart.shopcart')



@csrf_exempt
def weixin_login(request):
    #app = WxApp()
    #result = app.process(request.GET, request.body)
	if request.method == "GET":
		signature = request.GET.get('signature','')
		timestamp = request.GET.get('timestamp','')
		nonce = request.GET.get('nonce','')
		echostr = request.GET.get('echostr','')
		
		logger.debug('signature:%s' %(signature))
		logger.debug('timestamp:%s' %(timestamp))
		logger.debug('nonce:%s' %(nonce))
		logger.debug('echostr:%s' %(echostr))
		
		token = 'imycartweixinlogin'
		
		tmp_list = [token, timestamp, nonce]
		tmp_list.sort()
		tmp_str = "%s%s%s" % tuple(tmp_list)
		
		import hashlib
		tmp_str = hashlib.sha1(tmp_str.encode('utf8')).hexdigest()
		logger.debug('tmp_str:%s' %(tmp_str))
		if tmp_str == signature:
			return HttpResponse(echostr)
		else:
			return HttpResponse('Not Auth')
			
@csrf_exempt
def weixin_call_back(request):
	return HttpResponse('OK')
