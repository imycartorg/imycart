import types
from urllib import urlencode, urlopen
from hashcompat import md5_constructor as md5
from config import settings
from shopcart.models import SystemConfig

#�ַ�������봦��
def smart_str(s, encoding='utf-8', strings_only=False, errors='strict'):
	if strings_only and isinstance(s, (types.NoneType, int)):
		return s
	if not isinstance(s, basestring):
		try:
			return str(s)
		except UnicodeEncodeError:
			if isinstance(s, Exception):
				return ' '.join([smart_str(arg, encoding, strings_only,errors) for arg in s])
			return unicode(s).encode(encoding, errors)
	elif isinstance(s, unicode):
		return s.encode(encoding, errors)
	elif s and encoding != 'utf-8':
		return s.decode('utf-8', errors).encode(encoding, errors)
	else:
		return s

# ���ص�ַ
_GATEWAY = 'https://mapi.alipay.com/gateway.do?'


# ���������򲢳�ȥ�����еĿ�ֵ��ǩ������
# ������������Ӵ�
def params_filter(params):
	ks = params.keys()
	ks.sort()
	newparams = {}
	prestr = ''
	for k in ks:
		v = params[k]
		k = smart_str(k, settings.ALIPAY_INPUT_CHARSET)
		if k not in ('sign','sign_type') and v != '':
			newparams[k] = smart_str(v, settings.ALIPAY_INPUT_CHARSET)
			prestr += '%s=%s&' % (k, newparams[k])
	prestr = prestr[:-1]
	return newparams, prestr


# ����ǩ�����
def build_mysign(prestr, key, sign_type = 'MD5'):
	if sign_type == 'MD5':
		return md5(prestr + key).hexdigest()
	return ''


# ��ʱ���˽��׽ӿ�
def create_direct_pay_by_user(tn, subject, body, bank, total_fee):
	params = {}
	params['service']       = 'create_direct_pay_by_user'
	params['payment_type']  = '1'       #��Ʒ����ֻ��ѡ���
	
	# ��ȡ�����ļ�
	params['partner']           = SystemConfig.objects.get('ALIPAY_PARTNER').val
	params['seller_id']         = SystemConfig.objects.get('ALIPAY_KEY').val
	params['seller_email']      = SystemConfig.objects.get('ALIPAY_SELLER_EMAIL').val
	params['return_url']        = SystemConfig.objects.get('ALIPAY_RETURN_URL').val
	params['notify_url']        = SystemConfig.objects.get('ALIPAY_NOTIFY_URL').val
	params['_input_charset']    = SystemConfig.objects.get('ALIPAY_INPUT_CHARSET').val
	params['show_url']          = SystemConfig.objects.get('ALIPAY_SHOW_URL').val
	
	# �Ӷ��������ж�̬��ȡ���ı������
	params['out_trade_no']  = tn        # �������վ����ϵͳ�е�Ψһ������ƥ��
	params['subject']       = subject   # �������ƣ���ʾ��֧��������̨��ġ���Ʒ���ơ����ʾ��֧�����Ľ��׹���ġ���Ʒ���ơ����б��
	params['body']          = body      # ����������������ϸ��������ע����ʾ��֧��������̨��ġ���Ʒ�����������Ϊ��
	params['total_fee']     = total_fee # �����ܽ���ʾ��֧��������̨��ġ�Ӧ���ܶ���ȷ��С�������λ
	
	# ��չ���ܲ�������������ǰ
	if bank=='alipay' or bank=='':
		params['paymethod'] = 'directPay'   # ֧����ʽ���ĸ�ֵ��ѡ��bankPay(����); cartoon(��ͨ); directPay(���); CASH(����֧��)
		params['defaultbank'] = ''          # ֧����֧�������Ϊ��
	else:
		params['paymethod'] = 'bankPay'     # Ĭ��֧����ʽ���ĸ�ֵ��ѡ��bankPay(����); cartoon(��ͨ); directPay(���); CASH(����֧��)
		params['defaultbank'] = bank        # Ĭ���������ţ������б��http://club.alipay.com/read.php?tid=8681379        
	
	
	
	params,prestr = params_filter(params)
	
	params['sign'] = build_mysign(prestr, settings.ALIPAY_KEY, settings.ALIPAY_SIGN_TYPE)
	params['sign_type'] = settings.ALIPAY_SIGN_TYPE
	
	return _GATEWAY + urlencode(params)

def notify_verify(post):
	# ������֤--ǩ��
	_,prestr = params_filter(post)
	mysign = build_mysign(prestr, settings.ALIPAY_KEY, settings.ALIPAY_SIGN_TYPE)
	
	if mysign != post.get('sign'):
		return False
	
	# ������֤--��ѯ֧����������������Ϣ�Ƿ���Ч
	params = {}
	params['partner'] = settings.ALIPAY_PARTNER
	params['notify_id'] = post.get('notify_id')
	
	gateway = 'https://mapi.alipay.com/gateway.do?service=notify_verify&'
	verify_result = urlopen(gateway, urlencode(params)).read()
	if verify_result.lower().strip() == 'true':
		return True
	return False