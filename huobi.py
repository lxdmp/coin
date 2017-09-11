# coding=utf-8

import math
import json
from huobi import scene
from huobi import wallet
from huobi.common import KLine

def do_work(filename):

	# 载入行情
	infos = []
	with open(filename) as fd:
		content = fd.readline()
		data = json.loads(content)
		for i in range(len(data)):
			item = KLine(data[i])
			infos.append(item)
		fd.close()
	
	# 建立场景
	s = scene.Scene()

	st = 5
	mt = 10
	lt = 20
	
	# 添加指标
	s.addIndicator('ma_s', scene.MA(st))
	s.addIndicator('ma_m', scene.MA(mt))
	s.addIndicator('ma_l', scene.MA(lt))
	s.addIndicator('adx_m', scene.ADX(mt))
	
	# 结算器
	w = wallet.Wallet(100.0, 0.002, 0.002)

	# 绑定策略
	@s.bindStrategy(ctx=w)
	def strategy(scene, w):

		if len(scene.indicator('ma_s'))<2:
			return
		elif len(scene.indicator('ma_m'))<2:
			return
		elif len(scene.indicator('ma_l'))<2:
			return

		prev = 0
		actual = 1
		time = [scene.indicator('ma_s')[-2][0], scene.indicator('ma_s')[-1][0]]
		ma_s = [scene.indicator('ma_s')[-2][1], scene.indicator('ma_s')[-1][1]]
		ma_m = [scene.indicator('ma_m')[-2][1], scene.indicator('ma_m')[-1][1]]
		ma_l = [scene.indicator('ma_l')[-2][1], scene.indicator('ma_l')[-1][1]]
		
		'''
		持仓时,对adx,对一定的窗口宽度(short/2),若持续减弱,平仓
		'''
		width = int(math.ceil(st/2.0))
		if w.goods>0.0 and len(scene.indicator('adx_m'))>=width:
			buf = []
			for i in range(width):
				buf.append(scene.indicator('adx_m')[-width+i])
			match_this_case = True
			for i in range(len(buf)-1):
				if buf[i]<buf[i+1]:
					match_this_ase = False
					break
			if math_this_case:
				w.sell(time[actual], scene[-1].close, w.goods)
				return
				
			print 'adx at %s : %.2f' % \
				(scene.indicator('adx_m').last[0], scene.indicator('adx_m').last[1])

		'''
		持仓时,若趋势强度趋势与获取走势背离,考虑平仓.
		'''
		'''
		if w.goods>0.0:
			last_buy_order = w.buy_order(-1)
			if last_buy_order!=None:
				if_sell = wallet.SellOrder(time[actual], scene[-1].close, w.goods, w.sell_ratio)
				ratio = (if_sell.owned-last_buy_order.paid)/(last_buy_order.paid)
				print 'if sell at %s : %.2f%%' % (time[actual], ratio*100)
		'''



		if ma_s[prev]<ma_m[prev] and ma_s[actual]>=ma_m[actual] and \
			ma_s[actual]<ma_l[actual] and ma_l[actual]>=ma_l[prev]:
			w.buy(time[actual], scene[-1].close, w.available)
			return
		
		if ma_s[prev]>=ma_l[prev] and ma_s[actual]<ma_l[actual]:
			w.sell(time[actual], scene[-1].close, w.goods)
			return

	# 执行回测
	for i in range(len(infos)):
		info = infos[i]
		s.update(info)
	#print s
	print w

if __name__=='__main__':
	#do_work('btc_kline_005_json.json') # 对5min线测试
	#do_work('btc_kline_015_json.json') # 对15min线测试
	do_work('btc_kline_060_json.json') # 对小时线测试
	#do_work('btc_kline_100_json.json') # 对日线测试


