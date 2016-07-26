#ȷ��֧��
def pay(request):
	cbid=request.POST.get('id')
	try:
		cb=cBill.objects.get(id=cbid)
	except ObjectDoesNotExist:
		return HttpResponseRedirect("/err/no_object")
	
	#���������֧����
	if cb.cbank.gateway=='alipay':
			tn=cb.id
			subject=''
			body=''
			bank=cb.cbank.id
			tf='%.2f' % cb.amount
			url=create_direct_pay_by_user (tn,subject,body,bank,tf)
	
	#��������ǲƸ�ͨ
	elif cb.cbank.gateway=='tenpay':
		pass
	
	#ȥ֧��ҳ��
	return HttpResponseRedirect (url)

#alipay�첽֪ͨ

@csrf_exempt
def alipay_notify_url (request):
	if request.method == 'POST':
		if notify_verify (request.POST):
			#�̻���վ������
			tn = request.POST.get('out_trade_no')
			#֧��������
			trade_no=request.POST.get('trade_no')
			#����֧��״̬
			trade_status = request.POST.get('trade_status')
			cb = cBill.objects.get(pk=tn)
			
			if trade_status == 'TRADE_SUCCESS':
				cb.exe()
				log=Log(operation='notify1_'+trade_status+'_'+trade_no)
				log.save()
				return HttpResponse("success")
			else:
				#д����־
				log=Log(operation='notify2_'+trade_status+'_'+trade_no)
				log.save()
				return HttpResponse ("success")
		else:
			#�ڿ͹���
			log=Log(operation='hack_notify_'+trade_status+'_'+trade_no+'_'+'out_trade_no')
			log.save()
	return HttpResponse ("fail")

#ͬ��֪ͨ

def alipay_return_url (request):
	if notify_verify (request.GET):
		tn = request.GET.get('out_trade_no')
		trade_no = request.GET.get('trade_no')
		trade_status = request.GET.get('trade_status')
		
		cb = cBill.objects.get(pk=tn)
		log=Log(operation='return_'+trade_status+'_'+trade_no)
		log.save()
		return HttpResponseRedirect ("/public/verify/"+tn)
	else:
		#������ߺڿ͹���
		log=Log(operation='err_return_'+trade_status+'_'+trade_no)
		log.save()
		return HttpResponseRedirect ("/")


#�ⲿ��ת����������session���ܶ�ʧ���޷��ٽ���ϵͳ��
#�ͻ�����ͨ��xxx.com����������֧����ֻ�ܷ���www.xxx.com��������ͬ��session��ʧ��
def verify(request,cbid):
	try:
		cb=cBill.objects.get(id=cbid)
		#�������ʱ������ڳ���1�죬��ת������ҳ�棡
		#������վ��Ϣ��ʧ
		
		return render_to_response('public_verify.html',{'cb':cb},RequestContext(request))
	except ObjectDoesNotExist:
		return HttpResponseRedirect("/err/no_object")