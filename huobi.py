# coding=utf-8

import json
from huobi import scene,strategy
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
	
	# 回测
	s = scene.Scene()
	s.addIndicator('ma5', scene.MA(5))
	s.addIndicator('ma10', scene.MA(10))
	s.addIndicator('ma20', scene.MA(20))
	#m = strategy.Strategy()
	for i in range(len(infos)):
		info = infos[i]
		s.update(info)
		#m.update(m)
	#print m
	#print s

if __name__=='__main__':
	do_work('btc_kline_015_json.json')

