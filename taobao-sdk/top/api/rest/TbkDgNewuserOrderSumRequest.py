'''
Created by auto_sdk on 2018.06.07
'''
from top.api.base import RestApi
class TbkDgNewuserOrderSumRequest(RestApi):
	def __init__(self,domain='gw.api.taobao.com',port=80):
		RestApi.__init__(self,domain, port)
		self.activity_id = None
		self.adzone_id = None
		self.page_no = None
		self.page_size = None
		self.site_id = None

	def getapiname(self):
		return 'taobao.tbk.dg.newuser.order.sum'
