#coding=utf-8
from django.shortcuts import render,redirect
from shopcart.models import Product

from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def product_report(request):
	ctx = {}
	ctx['product_list'] = Product.objects.all()
	return render(request,'admin/product/report.html',ctx)