# coding=utf-8

# 场景
class Scene(object):

	def __init__(self):
		self.__infos = [] # 缓冲的行情(KLine)
		self.__ind = {} # 绑定的指标(BaseInd)

	def update(self, new_info):
		
		# 更新行情
		self.__infos.append(new_info)
		
		# 更新绑定的指标
		for k,v in self.__ind.iteritems():
			v.update(self)

	def addIndicator(self, name, new_ind):
		self.__ind[name] = new_ind

	@property
	def indicator(self, name):
		return self.ind[name]
	
	def __len__(self):
		return len(self.__infos)
	
	def __getitem__(self, key):
		if not isinstance(key, int):
			raise KeyError
		return self.__infos[key]

	@property
	def last(self):
		if len(self)>0:
			return self[-1]
		return None

	def __str__(self):
		ret = ''
		line = '\r\n'
		
		ret += '行情数据:'+line
		for i in range(len(self)):
			ret += str(self[i])+line
		ret += line

		for k,v in self.__ind.iteritems():
			ret += '指标%s数据:'%(k)+line
			ret += str(v)
			ret += line

		return ret

# 指标接口
class BaseInd(object):
	
	def __init__(self):
		pass
	
	def update(self, scene):
		pass

# MA
class MA(BaseInd):
	def __init__(self, interval):
		self.__interval = interval
		self.__infos = []
	
	@property
	def interval(self):
		return self.__interval

	def __len__(self):
		return len(self.__infos)

	def __getitem__(self, key):
		if not isinstance(key, int):
			raise KeyError
		return self.__infos[key]

	@property
	def last(self):
		if ken(self.__infos)<=0:
			return None
		item = self[-1]
		return (item[0], item[1])
			
	def update(self, scene):
		if len(scene)<self.interval:
			return
		sum = 0.0
		for i in range(self.interval):
			sum += scene[-i].close
		sum /= float(self.interval)
		new_item = [scene[-1].time, sum]
		self.__infos.append(new_item)

	def __str__(self):
		ret = ''
		for i in range(len(self)):
			item = self[i]
			ret += '%s %.2f\r\n' % (str(item[0]), item[1])
		return ret
		
