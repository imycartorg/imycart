#coding=utf-8
from django.shortcuts import render
from django.template.loader import render_to_string
from shopcart.models import System_Config,Product,Product_Images
from shopcart.utils import System_Para,my_pagination,get_system_parameters
import json,os
from django.http import JsonResponse
from django.utils.translation import ugettext as _
from django.http import Http404
from django.http import HttpResponse
# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger('imycart.shopcart')

# Create your views here.
def detail(request,id):
	ctx = {}
	ctx['system_para'] = get_system_parameters()
	ctx['page_name'] = 'Product'
	try:
		product = Product.objects.get(id=id)
	except Exception as err:
		logger.error('找不到编号为 %s 的商品。' % [id,])
		raise Http404
	#由于存在外键关系，只需要查出product对象，product所关联的images可以在模板中用product.images.all获得。
	ctx['product'] = product
	price_min = product.price
	price_max = product.price
	for attribut in product.attributes.all():
		if attribut.price_adjusment > 0:
			if attribut.price_adjusment + product.price > price_max:
				price_max = attribut.price_adjusment + product.price
		else:
			if product.price + attribut.price_adjusment < price_min:
				price_min = product.price + attribut.price_adjusment
	ctx['price_min'] = price_min
	ctx['price_max'] = price_max
	if price_max - price_min < 0.01:
		ctx['has_price_range'] = False
	else:
		ctx['has_price_range'] = True
		
	if request.method =='GET': #正常访问，返回动态页面
		#检查商品是否已经加入了用户的愿望清单
		if request.user.is_authenticated():
			wish_list = request.user.wishs.all()
			for wish in wish_list:
				if product == wish.product:
					logger.debug('The product which id is %s has been added to user\'s wishlist.' % (product.id))
					ctx['is_wished'] = True
		return render(request,System_Config.get_template_name() + '/product_detail.html', ctx)
	elif request.method == 'POST':#通过ajax访问，生成静态文件
		content = render_to_string(System_Config.get_template_name() + '/product_detail.html', ctx)
		result_dict = {}
		try:
			import codecs,os
			#先获取商品所属分类，作为目录
			category_list = product.categorys.all()
			f = None
			for cat in category_list:
				dir = 'static/' + cat.get_dirs()
				if not os.path.exists(dir):
					os.makedirs(dir)
				f = codecs.open(dir + product.static_file_name ,'w','utf-8')
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
		
def view_list(request):
	ctx = {}
	ctx['system_para'] = get_system_parameters()
	ctx['page_name'] = 'Product'
	
	if request.method =='GET':
		product_list = None
		if 'sort_by' in request.GET:
			if 'direction' in request.GET:
				if 'desc' == request.GET['direction']:
					product_list = Product.objects.order_by(request.GET['sort_by']).reverse()
				else:
					product_list = Product.objects.order_by(request.GET['sort_by'])
				
				ctx['direction'] = request.GET['direction']
			else:
				product_list = Product.objects.order_by(request.GET['sort_by'])
		else:
			logger.debug("all products")
			product_list = Product.objects.all()
		
		logger.debug("no sort_by")
		if 'page_size' in request.GET:
			page_size = request.GET['page_size']
		else:
			try:
				page_size = int(System_Config.objects.get(name='product_page_size'))
			except:
				page_size = 12
		
		product_list, page_range = my_pagination(request=request, queryset=product_list,display_amount=page_size)
		
		ctx['product_list'] = product_list
		ctx['page_range'] = page_range
		return render(request,System_Config.get_template_name() + '/product_list.html',ctx)


def query_product_show(request):
	ctx = {}
	ctx['system_para'] = get_system_parameters()
	ctx['page_name'] = 'Product'
	
	if request.method =='GET':
		query_condition = request.GET.get('query','')
		logger.debug('Query_String is %s ' % query_condition)
		from django.db.models import Q
		product_list = Product.objects.filter(Q(name__contains=query_condition))
		
		if 'page_size' in request.GET:
			product_list, page_range = my_pagination(request=request, queryset=product_list,display_amount=request.GET['page_size'])
		else:
			product_list, page_range = my_pagination(request=request, queryset=product_list)
		
		ctx['product_list'] = product_list
		ctx['page_range'] = page_range
		return render(request,System_Config.get_template_name() + '/product_list.html',ctx)
		
		
def ajax_get_product_info(request):
	logger.info('Entered the ajax_get_product_info function')
	product_to_get = json.loads((request.body).decode())

	logger.debug('product_id:%s' % [product_to_get['product_id']])
	product = Product.objects.get(id=product_to_get['product_id'])

	result_dict = {}
	result_dict['success'] = False
	result_dict['message'] = ''

	logger.debug('the attr_list length:%s' % [len(product_to_get['attr_list'])])
	logger.debug('the product.attributes length:%s' % [len(product.attributes.all())])
	
	#商品是否有额外属性
	if not product.attributes.all():
		#没有额外属性
		logger.info('Product has no extra attributes.')
		result_dict['success'] = True
		result_dict['message'] = null
		return result_dict	

	#attr是否已经全了
	pa = product.attributes.all()[0]
	attr_type_count = len(pa.attribute.all())
	logger.debug('Product has %s kinds attributes.' % [attr_type_count])

	
	para_list = product_to_get['attr_list']
	para_list = [int(attr) for attr in para_list]#转换成数值型
	para_list.sort() #排序
	logger.debug('>>>>para_list:' + str(para_list))
	
	attr_avaliable_set = set([])
	for pa in product.attributes.all():
		attr_id_list = [attr.id for attr in pa.attribute.all()]
		logger.debug('>>>>attr_id_list:' + str(attr_id_list))
		if set(para_list) <= set(attr_id_list):#判断para_list是否是attr_id_list的子集
			temp = set(attr_id_list) - set(para_list) #求差集
			if len(temp) == 0:
				#没有差集，已经选择全面了
				result_dict['success'] = True
				product_extra = {}
				product_extra['price'] = product.price + pa.price_adjusment
				product_extra['quantity'] = pa.quantity
				product_extra['sub_item_number'] = pa.sub_item_number
				product_extra['pa_id'] = pa.id
				#20160523，添加最小购买量
				product_extra['min_order_quantity'] = pa.min_order_quantity
				result_dict['message'] = product_extra
				return JsonResponse(result_dict)
			else:
				attr_avaliable_set = attr_avaliable_set | temp #求并集
	#进入到这里，说明前面没有选择全
	result_dict['success'] = False
	result_dict['message'] = list(attr_avaliable_set)#返回可以选择的attribute_id列表
	return JsonResponse(result_dict)

def ajax_get_product_description(request,id):
	logger.info('Entered the ajax_get_product_description function')
	product_desc = ''
	if request.is_ajax():
		try:
			product = Product.objects.get(id=id)
			product_desc = product.description
		except Exception as err:
			logger.error('检索id为%s的商品不存在.' % [id])
	return HttpResponse(product_desc)
	
