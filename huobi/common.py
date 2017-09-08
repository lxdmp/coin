# coding=utf-8

import datetime

class KLine(object):

	def __init__(self, l):
		assert(len(l)==6)
		self.__stamp = self.__format_stamp(l[0])
		self.__open = float(l[1])
		self.__high = float(l[2])
		self.__low = float(l[3])
		self.__close = float(l[4])
		self.__volume = float(l[5])
	
	def __format_stamp(self, s):
		s = str(s)
		yy = int(s[0:4])
		mm = int(s[4:6])
		dd = int(s[6:8])
		hh = int(s[8:10])
		mi = int(s[10:12])
		ss = 0
		return datetime.datetime(yy, mm, dd, hh, mi, ss)
	
	def __str__(self):
		return '%s : %.2f %.2f %.2f %.2f %.2f' % \
			(str(self.time), self.open, self.high, self.low, self.close, self.volume)

	@property
	def time(self):
		return self.__stamp
	
	@property
	def open(self):
		return self.__open

	@property
	def high(self):
		return self.__high

	@property
	def low(self):
		return self.__low

	@property
	def close(self):
		return self.__close

	@property
	def volume(self):
		return self.__volume

class Calculator(object):

	def __init__(self, ratio_b, ratio_s):
		self.buy_ratio = ratio_b# 扣币
		self.sell_ratio = ratio_s # 扣钱
	
	def target(self, fund_in, buy):
		buy_amount = fund_in/buy*(1-self.buy_ratio)
		target_sell = fund_in/buy_amount/(1-self.sell_ratio)
		return target_sell

	def profit(self, fund_in, buy, sell):
		buy_amount = fund_in/buy*(1-self.buy_ratio)
		fund_out = sell*buy_amount*(1-self.sell_ratio)
		profit_ratio = (fund_out-fund_in)/fund_in
		return (fund_out, profit_ratio)

if __name__=='__main__':
	import sys
	calc = Calculator()
	if len(sys.argv)==4:
		fund = float(sys.argv[1])
		buy_p = float(sys.argv[2])
		sell_p = float(sys.argv[3])
		target = calc.target(fund, buy_p)
		profit = calc.profit(fund, buy_p, sell_p)
		print 'target : %.3f' % (target)
		print 'profit : %.3f, %.3f%%' % (profit[0], profit[1]*100)

