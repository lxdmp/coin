# coding=utf-8

import datetime
import functools

class Order(object):

	def __init__(self, time):
		self.__time = time

	@property
	def time(self):
		'''
		单据时间
		'''
		return self.__time

class BuyOrder(Order):
	'''
	买单
	'''
	def __init__(self, time, price, paid, ratio):
		super(BuyOrder, self).__init__(time)
		self.__price = price
		self.__paid = paid
		self.__goods = paid/price*(1-ratio)

	@property
	def time(self):
		return super(BuyOrder, self).time

	@property
	def price(self):
		'''
		买入价
		'''
		return self.__price

	@property
	def paid(self):
		'''
		花费资金
		'''
		return self.__paid

	@property
	def goods(self):
		'''
		买入商品
		'''
		return self.__goods

class SellOrder(Order):
	'''
	卖单
	'''
	def __init__(self, time, price, goods, ratio):
		super(SellOrder, self).__init__(time)
		self.__price = price
		self.__goods = goods
		self.__owned = price*goods*(1-ratio)

	@property
	def time(self):
		return super(SellOrder, self).time
	
	@property
	def price(self):
		'''
		卖出价
		'''
		return self.__price

	@property
	def goods(self):
		'''
		卖出商品
		'''
		return self.__goods

	@property
	def owned(self):
		'''
		获取资金
		'''
		return self.__owned

class Wallet(object):

	def __init__(self, fund_init, ratio_b, ratio_s):
		self.__fund_init = fund_init # 初始资金
		self.__buy_ratio = ratio_b # 买入费率(扣币)
		self.__sell_ratio = ratio_s # 卖出费率(扣钱)
		
		self.__fund_left = fund_init # 剩余资金
		self.__goods = 0.0 # 交易商品
		self.__orders = [] # 交易记录{order:BuyOrder/SellOrder, ratio:ratio}
		self.__buy_order_idx = [] # 买单在缓存中索引集合
		self.__sell_order_idx = [] # 卖单在缓存中索引集合

	@property
	def buy_order_num(self):
		return len(self.__buy_order_idx)

	def buy_order(self, idx):
		try:
			return self.__orders[self.__buy_order_idx[idx]]['order']
		except Exception:
			return None

	@property
	def sell_order_num(self):
		return len(self.__sell_order_idx)


	def sell_order(self, idx):
		try:
			return self.__orders[self.__sell_order_idx[idx]]['order']
		except Exception:
			return None

	@property
	def sell_ratio(self):
		return self.__sell_ratio
	
	@property
	def buy_ratio(self):
		return self.__buy_ratio

	@property
	def cost(self):
		'''
		初始投入资金
		'''
		return self.__fund_init

	@property
	def available(self):
		'''
		可用资金
		'''
		return self.__fund_left

	@property
	def goods(self):
		'''
		持有商品
		'''
		return self.__goods

	def commutation(self, actual_price):
		'''
		当前资产值(商品以给定价格假设交易)
		'''
		cash_part = self.available
		goods_part = actual_price*self.goods*(1-self.__sell_ratio)
		return cash_part+goods_part

	def profit_ratio(self, actual_price):
		'''
		(相对初始投入资金)获利比率
		'''
		return self.commutation(actual_price)-self.cost/self.cost*100

	def can_buy(self, buyed):
		'''
		可否(花费一定资金)买入
		'''
		return self.available>=buyed and self.available>0.0

	def can_sell(self, selled):
		'''
		可否卖出(一定量的商品)
		'''
		return self.__goods>=selled and self.__goods>0.0
	
	def buy(self, time, price, paid):
		#print 'try to buy : %s %.2f %.2f' % (time, price, paid)
		if not self.can_buy(paid):
			#print 'try to buy but no fund'
			return False
		buy_order = BuyOrder(time, price, paid, self.__buy_ratio)
		self.__fund_left -= buy_order.paid
		self.__goods += buy_order.goods
		self.__orders.append({'order':buy_order, 'ratio':self.profit_ratio(price)})
		self.__buy_order_idx.append(len(self.__orders)-1)
		print 'buy successed at %s : use %.2f with price %.2f to goods %.6f' % \
			(time, paid, price, buy_order.goods)
		return True

	def sell(self, time, price, goods):
		#print 'try to sell : %s %.2f %.2f' % (time, price, volume)
		if not self.can_sell(goods):
			#print 'try to sell but no goods'
			return False
		sell_order = SellOrder(time, price, goods, self.__sell_ratio)
		self.__goods -= sell_order.goods
		self.__fund_left += sell_order.owned
		self.__orders.append({'order':sell_order, 'ratio':self.profit_ratio(price)})
		self.__sell_order_idx.append(len(self.__orders)-1)
		print 'sell successed at %s : use goods %.6f with price %.2f to own %.2f' % \
			(time, goods, price, sell_order.owned)
		return True

	def __str__(self):
		ret = ''
		for i in range(len(self.__orders)):
			order = self.__orders[i]['order']
			ratio = self.__orders[i]['ratio']
			if isinstance(order, BuyOrder):
				ret += '%s : buy at %.2f %.2f%%\r\n' % (order.time, order.price, ratio)
			elif isinstance(order, SellOrder):
				ret += '%s : sell at %.2f %.2f%%\r\n' % (order.time, order.price, ratio)
		return ret

