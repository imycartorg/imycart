#coding=utf-8
from django.shortcuts import render
from django.template.loader import render_to_string
from shopcart.models import System_Config,Article
from shopcart.utils import System_Para,my_pagination
import json,os
from django.http import JsonResponse
from django.http import Http404
from django.utils.translation import ugettext as _
# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger('imycart.shopcart')

# Create your views here.
def detail(request,id):
	ctx = {}
	ctx['system_para'] = System_Para.get_default_system_parameters()
	try:
		article = Article.objects.get(id=id)
	except:
		raise Http404
		
	ctx['article'] = article
		
	if request.method =='GET': #正常访问，返回动态页面
		return render(request,System_Config.get_template_name() + '/article.html', ctx)
	elif request.method == 'POST':#通过ajax访问，生成静态文件
		content = render_to_string(System_Config.get_template_name() + '/article.html', ctx)
		result_dict = {}
		try:
			import codecs,os
			#先获取商品所属分类，作为目录
			dir = 'static/' + article.folder
			if not os.path.exists(dir):
				os.makedirs(dir)
			f = codecs.open(dir + article.static_file_name ,'w','utf-8')
			f.write(content)
			f.close()
			result_dict['success'] = True
			result_dict['message'] = _('File already generated.')
		except Exception as err:
			logger.error('写文件失败。' + str(err))
			result_dict['success'] = False
			result_dict['message'] = _('File generate failed.')
		finally:
			if f is not None:
				f.close()
		return JsonResponse(result_dict)