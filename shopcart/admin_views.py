#coding=utf-8
from django.shortcuts import render,redirect
from shopcart.models import Product,System_Config,Product_Images,Album
from shopcart.utils import System_Para,handle_uploaded_file
from django.http import Http404,HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
import logging
# Get an instance of a logger
logger = logging.getLogger('imycart.shopcart')

@staff_member_required
def product_report(request):
	ctx = {}
	ctx['product_list'] = Product.objects.all()
	return render(request,'admin/product/report.html',ctx)
	
@staff_member_required
@csrf_exempt
def file_upload(request,item_type,item_id):
	ctx = {}
	ctx['system_para'] = System_Para.get_default_system_parameters()
	ctx['action_url'] = '/file-upload/' + item_type + '/' + item_id + "/"
	ctx['file_delete_url'] = '/file-delete/' + item_type
	ctx['host_item_id'] = item_id
	if request.method == 'GET':
		if item_type == 'product' or item_type == 'product_album':
			try:
				item = Product.objects.get(id=item_id)
				ctx['item'] = item
				try:
					ctx['image_list'] = Product_Images.objects.filter(product=item).order_by('create_time').reverse()
					if item_type == 'product_album':
						ctx['image_list'] = Album.objects.filter(item_type=item_type,item_id=item.id).order_by('create_time').reverse()
				except:
					ctx['image_list'] = []
			except:
				raise Http404
		elif item_type == 'article':
			raise Http404
		else:
			raise Http404
		return render(request,System_Config.get_template_name() + '/file_upload.html',ctx)
	else:
		logger.debug('>>>>>1')
		if item_type == 'product' or item_type == 'product_album':
			logger.debug('>>>>>2')
			try:
				logger.debug('>>>>>3')
				item = Product.objects.get(id=item_id)
				logger.debug('>>>>>4')
			except:
				raise Http404
			logger.debug('>>>>>5')
			filenames = handle_uploaded_file(request.FILES['upload'],item_type,item_id)
			logger.debug('>>>>>6')
			#加入到对象的图片列表中去
			logger.debug('>>>>>7')
			if item_type == 'product':
				logger.debug('>>>>>8')
				pi = Product_Images.objects.create(image=filenames['image_url'],thumb=filenames['thumb_url'],product=item)
				logger.debug('>>>>>9')
			else:
				logger.debug('>>>>>10')
				ai = Album.objects.create(image=filenames['image_url'],thumb=filenames['thumb_url'],item_type=item_type,item_id=item.id)
				logger.debug('>>>>>11')
		elif item_type == 'article':
			raise Http404
		else:
			raise Http404
		#判断是否是从CKEDITER传上来的
		if 'CKEditorFuncNum' in request.GET:
			logger.debug('请求来自CKEDITER.')
			script = '<script type=\"text/javascript\">window.parent.CKEDITOR.tools.callFunction("' + request.GET['CKEditorFuncNum'] + '","' + filenames['image_url'] + '");</script>';
			logger.debug('返回的script： %s' % [script])
			return HttpResponse(script,content_type='text/html;charset=UTF-8')
		return redirect('/file-upload/' + item_type + '/' + item_id + "/")
		
@staff_member_required
def file_delete(request,item_type,item_id,host_item_id):
	ctx = {}
	ctx['system_para'] = System_Para.get_default_system_parameters()
	ctx['file_delete_url'] = '/file-delete/' + item_type
	if request.method == 'GET':
		try:
			if item_type == 'product':
				image = Product_Images.objects.get(id=item_id)
				image.delete()
			elif item_type == 'product_album':
				image = Album.objects.get(id=item_id)
				image.delete()
			elif item_type == 'article':
				raise Http404
			else:
				raise Http404
		except:
			raise Http404
		return redirect('/file-upload/' + item_type + '/' + host_item_id + "/")
		
@staff_member_required
def ckediter(request,item_type,item_id):
	ctx = {}
	ctx['system_para'] = System_Para.get_default_system_parameters()
	ctx['upload_url'] = '/file-upload/' + item_type + '/' + item_id + '/'
	return render(request,'admin/ckediter.html',ctx)
	