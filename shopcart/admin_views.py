#coding=utf-8
from django.shortcuts import render,redirect
from shopcart.models import Product,System_Config,Product_Images,Album,Article
from shopcart.forms import product_add_form
from shopcart.utils import System_Para,handle_uploaded_file
from django.http import Http404,HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
import logging
# Get an instance of a logger
logger = logging.getLogger('imycart.shopcart')

@staff_member_required
def product_opration(request,opration,id):
	ctx = {}
	ctx['system_para'] = System_Para.get_default_system_parameters()
	if request.method == 'GET':
		if opration == 'add':
			if id != '0':
				ctx['image_upload_url'] = '/file-upload/product/%s/' % id
				ctx['edit_url'] = '/admin/shopcart/product/%s/change/' % id
			return render(request,'admin/product/add.html',ctx)
		else:
			raise Http404
	elif request.method == 'POST':
		if opration == 'add':
			form = product_add_form(request.POST)
			if form.is_valid():
				product = form.save()
				logger.debug('product id: %s' % product.id)
				return redirect('/admin/product/add/%s' % product.id)
			else:
				logger.error('form is not valid')
	else:
		raise Http404

@staff_member_required
def product_make_static(request):
	ctx = {}
	ctx['product_list'] = Product.objects.all()
	return render(request,'admin/product/make_static.html',ctx)
	
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
		if item_type == 'product' or item_type == 'product_album':
			try:
				item = Product.objects.get(id=item_id)
			except:
				raise Http404
				
			manual_name = request.POST.get('manual_name','noname')	
			same_name_handle = request.POST.get('same_name_handle','reject')
						
			filenames = handle_uploaded_file(request.FILES['upload'],item_type,item_id,request.POST['filename_type'],manual_name,same_name_handle)
			if filenames['upload_result'] == False:
				return HttpResponse(filenames['upload_error_msg'])
				
			#加入到对象的图片列表中去
			if item_type == 'product':
				pi = Product_Images.objects.create(image=filenames['image_url'],thumb=filenames['thumb_url'],product=item)
			else:
				ai = Album.objects.create(image=filenames['image_url'],thumb=filenames['thumb_url'],item_type=item_type,item_id=item.id)
		elif item_type == 'article':
			try:
				item = Article.objects.get(id=item_id)
			except:
				raise Http404
			filenames = handle_uploaded_file(request.FILES['upload'],item_type,item_id,request.POST['filename_type'],manual_name,same_name_handle)
			if filenames['upload_result'] == False:
				return HttpResponse(filenames['upload_error_msg'])			
		
			ai = Album.objects.create(image=filenames['image_url'],thumb=filenames['thumb_url'],item_type=item_type,item_id=item.id)
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
	ctx['article_content'] = ''
	ctx['id'] = item_id
	if request.method == 'GET':
		try:
			if item_type == 'product':
				ctx['article_content'] = Product.objects.get(id=item_id).description
			elif item_type == 'article':
				ctx['article_content'] = Article.objects.get(id=item_id).content
			else:
				raise Http404
		except:
			raise Http404
		return render(request,'admin/ckediter.html',ctx)

def product_edit(request,id):
	logger.info('Enter into the product_edit function.')
	if request.method=='POST':
		try:
			product = Product.objects.get(id=id)
			product.description = request.POST['editor']
			product.save()
			return HttpResponse('成功')
		except Exception as err:
			logger.error('The Product which id is %s can not found.' % [id])
			raise Http404
	else:
		raise Http404