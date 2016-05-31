# -*- coding: UTF-8 –*-
# Create your views here.
from django.http import HttpResponse
from shopcart.models import System_Config
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
		
		token = System_Config.objects.get(name='weixin_token').val
		tmp_str = signature(nonce,timestamp,token)
		
		if tmp_str == signature:
			return HttpResponse(echostr)
		else:
			return HttpResponse('Not Auth')


			
def signature(nonce,timestamp,token):
	tmp_list = [token, timestamp, nonce]
	tmp_list.sort()
	tmp_str = "%s%s%s" % tuple(tmp_list)
	
	import hashlib
	tmp_str = hashlib.sha1(tmp_str.encode('utf8')).hexdigest()
	logger.debug('tmp_str:%s' %(tmp_str))
	return tmp_str
			
@csrf_exempt
def weixin_call_back(request):
	#用code换取access_tokon
	#https://api.weixin.qq.com/sns/oauth2/access_token?appid=APPID&secret=SECRET&code=CODE&grant_type=authorization_code
	
	app_id = System_Config.objects.get(name='weixin_appid').val
	code = request.GET.get('code','')
	logger.debug('获得的code:%s' % (code))
	secret = System_Config.objects.get(name='weixin_app_secret').val
	import http.client
	httpClient = None	
	try:
		httpClient = http.client.HTTPSConnection('api.weixin.qq.com', 443, timeout=30)
		url = '/sns/oauth2/access_token?appid=%(app_id)s&secret=%(secret)s&code=%(code)s&grant_type=authorization_code' % {'app_id':app_id,'secret':secret,'code':code}
		logger.debug('url:%s' % (url))
		httpClient.request('GET', url)
	
		#response是HTTPResponse对象
		response = httpClient.getresponse()
		logger.debug('response.status:%s' %(response.status))
		logger.debug('response.reason:%s' %(response.reason))
		response_body = response.read()
		logger.debug('response.read():%s' %(response_body))
		
		
		import json
		#拉取用户信息
		#https://api.weixin.qq.com/sns/userinfo?access_token=ACCESS_TOKEN&openid=OPENID&lang=zh_CN
		token_info = json.loads((response_body).decode())
		logger.debug(str(token_info))
		logger.debug('openid:%s' % (token_info['openid']))
		logger.debug('token:%s' % (token_info['access_token']))
		
		logger.debug('start to get user info...')
		get_user_info_request = http.client.HTTPSConnection('api.weixin.qq.com', 443, timeout=30)
		url = '/sns/userinfo?access_token=%(token)s&openid=%(openid)s&lang=zh_CN' % {'token':token_info['access_token'],'openid':token_info['openid']}
		logger.debug('url:%s' %(url))
		get_user_info_request.request('GET',url)
		
		get_user_info_response = get_user_info_request.getresponse()
		logger.debug('response.status:%s' %(get_user_info_response.status))
		logger.debug('response.reason:%s' %(get_user_info_response.reason))
		get_user_info_response_body = get_user_info_response.read()
		logger.debug('response.read():%s' %(get_user_info_response_body))
		
		user_info = json.loads((get_user_info_response_body).decode())
		logger.debug('nickname:%s' %(user_info['nickname']))
		logger.debug('headimgurl:%s' % (user_info['headimgurl']))
		return HttpResponse('<h1>昵称：%s<h1><br><img src="%s" />' % (user_info['nickname'],user_info['headimgurl']))
		
	except Exception as e:
		logger.error(str(e))
	finally:
		if httpClient:
			httpClient.close()
			
		if get_user_info_request:
			get_user_info_request.close()
	
	return HttpResponse('OK')
