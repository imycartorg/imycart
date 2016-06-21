from django.contrib import admin

from shopcart.models import Product,Order,Order_Products,Category,System_Config,Attribute,Attribute_Group,Article,Email_List,Product_Attribute,Express,Inquiry,Product_Images

# Register your models here.
class InquiryAdmin(admin.ModelAdmin):
	list_display = ('name', 'email', 'company','create_time','update_time') 
	list_filter = ('create_time',)
	#自然是排序所用了，减号代表降序排列
	ordering = ('-create_time',)
admin.site.register(Inquiry,InquiryAdmin)


# Register your models here.
class ExpressAdmin(admin.ModelAdmin):
	list_filter = ('create_time',)
	#自然是排序所用了，减号代表降序排列
	ordering = ('-create_time',)
admin.site.register(Express,ExpressAdmin)

class EmailListAdmin(admin.ModelAdmin):
	list_filter = ('create_time',)
	#自然是排序所用了，减号代表降序排列
	ordering = ('-create_time',)
admin.site.register(Email_List,EmailListAdmin)

class ArticleAdmin(admin.ModelAdmin):
	list_filter = ('create_time',)
	#自然是排序所用了，减号代表降序排列
	ordering = ('-create_time',)
admin.site.register(Article,ArticleAdmin)


class Attribute_GroupAdmin(admin.ModelAdmin):
	list_filter = ('create_time',)
	list_display = ('name', 'code','group_type','create_time','update_time') 
	#自然是排序所用了，减号代表降序排列
	ordering = ('-create_time',)
admin.site.register(Attribute_Group,Attribute_GroupAdmin)

class AttributeAdmin(admin.ModelAdmin):
	list_filter = ('create_time',)
	list_display = ('name', 'code','group','create_time','update_time') 
	#自然是排序所用了，减号代表降序排列
	ordering = ('-create_time',)
admin.site.register(Attribute,AttributeAdmin)

class System_ConfigAdmin(admin.ModelAdmin):
	list_display = ('name', 'val','create_time','update_time') 
	search_fields = ('name', 'val')
	list_filter = ('create_time',)
	#自然是排序所用了，减号代表降序排列
	ordering = ('-create_time',)
admin.site.register(System_Config,System_ConfigAdmin)


class CategoryAdmin(admin.ModelAdmin):
	list_display = ('code', 'name', 'sort_order','parent','create_time','update_time') 
	search_fields = ('code', 'name')
	list_filter = ('create_time',)
	#自然是排序所用了，减号代表降序排列
	ordering = ('-create_time',)
admin.site.register(Category,CategoryAdmin)


class ProductAdmin(admin.ModelAdmin):
	list_display = ('item_number', 'name', 'quantity','warn_quantity','price','market_price','keywords','short_desc','create_time','update_time')
	search_fields = ('item_number', 'name')
	list_filter = ('create_time',)
	ordering = ('-create_time',)	
admin.site.register(Product,ProductAdmin)


class Product_ImagesAdmin(admin.ModelAdmin):
	list_display = ('product', 'is_show_in_product_detail', 'sort','thumb','create_time','update_time')
	search_fields = ('item_number', 'name')
	list_filter = ('create_time',)
	ordering = ('-create_time',)	
admin.site.register(Product_Images,Product_ImagesAdmin)


class ProductAttributeAdmin(admin.ModelAdmin):
	list_display = ('product','name','sub_item_number', 'quantity','price_adjusment','create_time','update_time')
	list_filter = ('create_time',)
	#自然是排序所用了，减号代表降序排列
	ordering = ('-create_time',)
admin.site.register(Product_Attribute,ProductAttributeAdmin)

#class Order_ProductsInline(admin.StackedInline):
class Order_ProductsInline(admin.TabularInline):
	model = Order_Products
	fields = ['product_id','name','price','quantity']
	#fields = ['order_number', 'user','status','shipping_status']
	#extra = 3

class OrderAdmin(admin.ModelAdmin):
	#编辑页
	#fields = ['order_number', 'user','status','shipping_status']
	fieldsets = [
		('订单基本信息',{'fields':['order_number', 'user','status','shipping_status']}),
	]
	inlines = [Order_ProductsInline]

	#列表页，列表顶部显示的字段名称
	list_display = ('order_number', 'user', 'status','shipping_status','create_time','update_time','get_human_status') 
	#列表页出现搜索框，参数是搜索的域
	search_fields = ('order_number', 'status')
	#右侧会出现过滤器，根据字段类型，过滤器显示过滤选项
	list_filter = ('create_time','status',)
	#页面中的列表顶端会有一个逐层深入的导航条，逐步迭代选项
	date_hierarchy = 'create_time'
	#自然是排序所用了，减号代表降序排列
	ordering = ('-create_time',)
 
#将Author模块和管理类绑定在一起，注册到后台管理
admin.site.register(Order, OrderAdmin)



