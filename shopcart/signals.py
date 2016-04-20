from django.dispatch import Signal

# 用户注册的相关消息
user_registration_success = Signal()

# 用户密码修改成功的相关消息
user_password_modify_applyed = Signal()
user_password_modify_success = Signal()

#商品的相关消息
product_added_to_cart = Signal()
product_added_to_wishlist = Signal()
product_price_changed = Signal()
product_quantity_warn = Signal()

#订单
order_was_placed = Signal()
order_was_canceled = Signal()
order_was_shipped = Signal()
order_was_complete = Signal()

