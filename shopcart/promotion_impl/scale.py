#coding=utf-8
import logging
logger = logging.getLogger('imycart.shopcart')

# 折扣优惠实现类
def calculate(request,promotion):
	user = request.user
	
	
	
	return user.email + 'OFF 20%,Yeah!'
	
		
