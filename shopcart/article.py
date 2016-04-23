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
		
def view_blog_list(request):
	ctx = {}
	ctx['system_para'] = System_Para.get_default_system_parameters()
	
	if request.method =='GET':
		product_list = None
		if 'sort_by' in request.GET:
			if 'direction' in request.GET:
				if 'desc' == request.GET['direction']:
					article_list = Article.objects.filter(category=Article.ARTICLE_CATEGORY_BLOG).order_by(request.GET['sort_by']).reverse()
				else:
					article_list = Article.objects.filter(category=Article.ARTICLE_CATEGORY_BLOG).order_by(request.GET['sort_by'])
			else:
				article_list = Article.objects.filter(category=Article.ARTICLE_CATEGORY_BLOG).order_by(request.GET['sort_by'])
		else:
			article_list = Article.objects.filter(category=Article.ARTICLE_CATEGORY_BLOG)
		
		if 'page_size' in request.GET:
			article_list, page_range = my_pagination(request=request, queryset=article_list,display_amount=request.GET['page_size'])
		else:
			article_list, page_range = my_pagination(request=request, queryset=article_list)
		
		ctx['article_list'] = article_list
		ctx['page_range'] = page_range
		return render(request,System_Config.get_template_name() + '/blog_list.html',ctx)