jQuery(document).ready(function() {
    "use strict";
	// Django需要验证csrf信息验证提交人身份，这段代码必须，需要放入公共JS
	// csrf信息开始
		function getCookie(name) {
			var cookieValue = null;
			if (document.cookie && document.cookie != '') {
				var cookies = document.cookie.split(';');
				for (var i = 0; i < cookies.length; i++) {
					var cookie = jQuery.trim(cookies[i]);
					// Does this cookie string begin with the name we want?
					if (cookie.substring(0, name.length + 1) == (name + '=')) {
						cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
						break;
					}
				}
			}
			return cookieValue;
		}
		var csrftoken = getCookie('csrftoken');
	
		function csrfSafeMethod(method) {
			// these HTTP methods do not require CSRF protection
			return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
		}
		$.ajaxSetup({
			beforeSend: function(xhr, settings) {
				if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
					xhr.setRequestHeader("X-CSRFToken", csrftoken);
				}
			}
		});
		// csrf信息结束
});


/***
	Common functions
***/
$(function(){
    $.ajaxSetup ({
        cache: false //关闭AJAX缓存
    });
});

//公共的调用ajax方法
function imycartAjaxCall(url,object,is_show_message_box,message){
	var encodedata = $.toJSON(object);
	$.ajax({
			type : 'POST',
			contentType : 'application/json',
			dataType : 'json',
			url : url,
			data : encodedata,
			success : function(result) {
				if(result.success==true){
					if(is_show_message_box){
						if(message==null){
							message = "Your opration is success."
						}
						$("#infoMessage").html(message);
					}
				}else{
					if(message==null){
							message = "Your opration is failed."
					}
					$("#infoMessage").html(message);
				}
				$("#myModal").modal('toggle');
			},
			error : function(result) {
				alert(result.success);
			}
	});
};
//带回调函数的ajax请求通用方法
function imycartAjaxCallWithCallback(url,object,callback,triggerControl,extraInfo){
	var encodedata = $.toJSON(object);
	$.ajax({
			type : 'POST',
			contentType : 'application/json',
			dataType : 'json',
			url : url,
			data : encodedata,
			success : function(result) {
				callback(result,triggerControl,extraInfo)
			},
			error : function(result) {
				alert(result.success);
			}
	});
};

//刷新验证码
jQuery(".next-captcha").click(function(){
	event.preventDefault();
	$.getJSON('/refresh-captcha', function(json) {  
		// This should update your captcha image src and captcha hidden input  
		// debugger; 
		var status = json['status'];  
		var new_cptch_key = json['new_cptch_key'];  
		var new_cptch_image = json['new_cptch_image'];  
		id_captcha_0 = $("#id_reg_captcha_0");  
		img = $(".captcha");  
		id_captcha_0.attr("value", new_cptch_key);  
		img.attr("src", new_cptch_image);  
	});   
});

//ajax验证验证码
jQuery('.form-control-captcha').blur(function(){
	key_id = $(this).data('captcha-key')
	json_data={'response':$(this).val(),  
		// 获取输入框和隐藏字段id_captcha_0的数值            
			'hashkey':$('#' + key_id).val()        
	};
	
	$.getJSON('/ajax_val_captcha', json_data, function(data){ //ajax发送            
		$('#captcha_status').remove();            
		if(data['success'] == true){ //status返回1为验证码正确， status返回0为验证码错误， 在输入框的后面写入提示信息               
			alert(data['message']);        
		}else{
			alert(data['message']);
			//$(this).after('<span id="captcha_status" >*' + data['message'] + '</span>')     
		}        
	});     
});

/***
 ***   页面跳转类开始
 ***/
jQuery("#CreateAccount").click(function(event) {
		location.href = "/user/register";
}); 

jQuery(".return-to-cart").click(function() {
	var url = "/cart/show";
	location.href = url;
});
/***
 ***   页面跳转类结束
 ***/
 
 

/***
 ***  查看购物车明细页面使用的方法开始 ***
 ***/
function imycartModifyCart(method,cart_id,quantity,triggerControl){
	url = '/cart/modify';
	var cart = new Object();
	cart.method = method;
	cart.cart_id = cart_id;
	cart.quantity = quantity;
	
	extraInfo = new Object();
	extraInfo.method = method;
	imycartAjaxCallWithCallback(url,cart,imycartModifyCartCallback,triggerControl,extraInfo);
}

function imycartModifyCartCallback(result,triggerControl,extraInfo){
	if(extraInfo.method=="set"){
		//先获取出发事件的数量控件旁边的金额字段的span控件
		var td = triggerControl.parent().siblings("[name=subTotalTd]");
		var subTotal = td.find("span");
		subTotal.html("$ " + result.cart_product_total.toFixed(2));
	}else if(extraInfo.method == "del"){
		var tr = triggerControl.parent().parent();	
		tr.remove();
	}else if(extraInfo.method == "clear"){
		//都清空
		$("#shopping-cart-table").find("tbody").find("tr").remove();
		$("#shopping-cart-table").find("tbody").html("<tr><td class='a-center'><span><span>Your shopping cart is empty!</span></span></td></tr>");
	}

	//更新总金额
	imycartUpdateTotalAmount(result.sub_total,result.sub_total);
}

function imycartUpdateTotalAmount(totalAmount,totalPrice){
	//更新商品总价、总运费、总金额
	$("#totalPrice").html("$ " + totalPrice.toFixed(2));
	$("#totalAmount").html("$ " + totalAmount.toFixed(2));
}
/***
 ***  查看购物车明细页面使用的方法结束 ***
 ***/
//付款按钮
jQuery(".order-pay-button").click(function(event) {
	var url = '/cart/payment/' + $(this).data("id");
	location.href = url;
}); 
 
 
//取消订单
jQuery(".order-cancel-button").click(function(event) {
	var url = '/order/cancel';
	var object = new Object();
	object.order_id = $(this).data("id");
	
	var extraInfo = new Object();
	extraInfo.method = 'cancel';
	extraInfo.order_id = object.order_id;
	imycartAjaxCallWithCallback(url,object,imycartChangeOrderCallBack,$(this),extraInfo)	
}); 


function imycartChangeOrderCallBack(result,triggerControl,extraInfo){
	if(extraInfo.method=='cancel'){
		//删除自己这一行
		condition = "[title=" + "container_order_" + extraInfo.order_id + "]";
		$(condition).remove();
	}
}


//把商品添加到购物车	
jQuery("#addToCartBtn").click(
	function() {
		var productId = $(this).data("product-id");
		var product_attribute_id = $("#product-attribute-id").val();
		imycartAddProductToCartaddProductToCart(productId,product_attribute_id,$("#qty").val());
	}
);

function imycartAddProductToCartaddProductToCart(product_id,product_attribute_id,quantity){
		var url = "/cart/add";
		var cart = new Object();
		cart.product_id = product_id;
		cart.product_attribute_id = product_attribute_id;
		cart.quantity = quantity;
		imycartAjaxCall(url,cart,true,null);
};

//把商品添加到愿望清单
jQuery("#addToWishList").click(
	function() {
		event.preventDefault();
		imycartAddProductToWishlist($(this).data("product-id"));
	}
);
function imycartAddProductToWishlist(product_id) {
	var url = "/wishlist/add";
	var wish = new Object();
	wish.product_id = product_id;
	imycartAjaxCall(url,wish,true,null);
};

//选择了商品某个额外属性
jQuery(".product-attribute-item").click(function(){
		var product_to_get = new Object();
		product_to_get.product_id = $(this).data("product-id");
		condition = ".product-attribute-group-selected[title=" + $(this).data("group-code") + "]";		
		$(condition).val($(this).data("attribute-id"));
		var attr_list = new Array();
		$(".product-attribute-group-selected").each(function(){
			if($(this).val() != ""){
				attr_list.push($(this).val());
			}
			
		});
		product_to_get.attr_list = attr_list;
		var url = '/product/get-product-extra/'
		var encodedata = $.toJSON(product_to_get);
		$.ajax({
				type : 'POST',
				contentType : 'application/json',
				dataType : 'json',
				url : url,
				data : encodedata,
				success : function(result) {
						if(result.success==true){
							$("#product-attribute-id").val(result.message.pa_id);
							//确定价格
							$("#product-price-main").text("$" + result.message.price.toFixed(2));
						}else{
							//设定可以选择的属性列表
							alert('Attributs avaliable to select are:' + result.message)
						
						}
						//alert('pa_id:' + $("input[name=product-attribute-id]").val());
				},
				error : function(result) {
					alert(result.success);
				}
		});
});