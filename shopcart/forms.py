# -*- coding:utf-8 -*-
from django import forms
from shopcart.models import MyUser,Address
from captcha.fields import CaptchaField
from django.utils.translation import ugettext as _

#只验证captcha字段的form
class captcha_form(forms.Form):
	captcha = CaptchaField()

class register_form(forms.ModelForm):
	captcha = CaptchaField()
	class Meta:
		model = MyUser
		fields = ('email','password',) 
		
class address_form(forms.ModelForm):
	tel = forms.CharField(required=False)
	mobile = forms.CharField(required=False)
	sign_building = forms.CharField(required=False)
	class Meta:
		model = Address
		fields = ('useage','is_default','first_name','last_name','country','province','city','district','address_line_1','address_line_2','zipcode','tel','mobile','sign_building') 
