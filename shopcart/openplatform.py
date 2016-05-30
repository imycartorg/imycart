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
	#用code换取access_tokon
	#https://api.weixin.qq.com/sns/oauth2/access_token?appid=APPID&secret=SECRET&code=CODE&grant_type=authorization_code
	""" httplib发送https的post请求
	headers = {"Content-type": "application/x-www-form-urlencoded; charset=UTF-8", 
	"Accept": "*/*"} 
	params = {'username':'xxxx'}         
	data = urllib.urlencode(params)         
	host = '127.0.0.1' 
	url = '/login' 
	conn = httplib.HTTPSConnection(host) 
	conn.request('POST', url, data, headers)
	
	
	import httplib
	httpClient = None	
	try:
		httpClient = httplib.HTTPConnection('localhost', 80, timeout=30)
		httpClient.request('GET', '/test.php')
	
		#response是HTTPResponse对象
		response = httpClient.getresponse()
		print response.status
		print response.reason
		print response.read()
	except Exception, e:
		print e
	finally:
		if httpClient:
			httpClient.close()
	"""
	
	app_id = 'wx3a86e89b09a7c875'
	code = request.GET.get('code','')
	logger.debug('获得的code:%s' % (code))
	secret = ''
	import http.client
	httpClient = None	
	try:
		httpClient = http.client.HTTPConnection('api.weixin.qq.com', 80, timeout=30)
		url = '/sns/oauth2/access_token?appid=%(app_id)s&secret=%(secret)s&code=%(code)s&grant_type=authorization_code' % {'app_id':app_id,'secret':secret,'code':code}
		logger.debug('url:%s' % (url))
		httpClient.request('GET', url)
	
		#response是HTTPResponse对象
		response = httpClient.getresponse()
		logger.debug('response.status:%s' %(response.status))
		logger.debug('response.reason:%s' %(response.reason))
		logger.debug('response.read():%s' %(response.read()))
	except Exception as e:
		logger.error(e)
	finally:
		if httpClient:
			httpClient.close()	
	return HttpResponse('OK')
