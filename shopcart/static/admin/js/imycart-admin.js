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
							message = "Your opration is success.";
						}else if(message=='showservermessage'){
								message = result.message;
						}
						$("#infoMessage").html(message);
					}
				}else{
					if(message==null){
							message = "Your opration is failed.";
					}else if(message=='showservermessage'){
							message = result.message;
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
				callback(result,triggerControl,extraInfo);
			},
			error : function(result) {
				alert(result.success);
			}
	});
};

//公共方法
jQuery("#main-content-checkbox-all").click(function(e){
	if($("#main-content-checkbox-all").is(":checked")){
		//从没选中到选中
		//alert("1");
		$("#test_oper").attr("checked","true");
		//$("#main-content-table").find("input[type='checkbox']").each(function(){
		//	$(this).attr("checked","checked");
		//});
	}else{
		$("#test_oper").removeAttr("checked");
		$("#main-content-table").find("input[type='checkbox']").each(function(){
			$(this).attr("checked",false);
		});
	}
	
});


//订单管理界面
jQuery("#order_batch_delete").click(function(e){
	var id_list = [];
	 $("input[name='is_oper']").each(function(){
		if($(this).is(':checked')){
			id_list.push($(this).data("order-id"));
		}
	});
	var oper_ids = id_list.join(',');
	$("#oper-ids").val(oper_ids);
	$("#order_oper_form").submit();
});

