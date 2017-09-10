# coding=utf-8
import math
import functools

# 场景
class Scene(object):

	def __init__(self):
		self.__infos = [] # 缓冲的行情(KLine)
		self.__ind = {} # 绑定的指标(name : BaseInd)
		self.__strategy = [] # 绑定的策略([prio(int), impl])

	def update(self, new_info):
		
		# 更新行情
		self.__infos.append(new_info)
		
		# 更新绑定的指标
		for k,v in self.__ind.iteritems():
			v.update(self)

		# 更新策略
		for i in range(len(self.__strategy)):
			strategy = self.__strategy[i]
			strategy[1](self, strategy[2])
	
	def addIndicator(self, name, new_ind):
		self.__ind[name] = new_ind

	def bindStrategy(self, prio=0, ctx=None):
		def wrapper_arg(func):
			@functools.wraps(func)
			def wrapper(*args, **kwargs):
				result = func(*args, **kwargs)
				return result
			new_item = [prio, wrapper, ctx]
			self.__strategy.append(new_item)
			sorted(self.__strategy, key=lambda item:item[0])
			return wrapper
		return wrapper_arg

	def indicator(self, name):
		return self.__ind[name]
	
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

# MA指标(Moving Averagr)
class MA(BaseInd):
	def __init__(self, interval=10):
		super(MA, self).__init__()
		self.__interval = interval
		self.__infos = [] # [0:时间,1:ma数据]
	
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
		if len(self.__infos)<=0:
			return None
		item = self[-1]
		return (item[0], item[1])
			
	def update(self, scene):
		if len(scene)<self.interval:
			return
		sum = 0.0
		for i in range(self.interval):
			sum += scene[-i-1].close
		sum /= float(self.interval)
		new_item = [scene[-1].time, sum]
		self.__infos.append(new_item)

	def __str__(self):
		ret = ''
		for i in range(len(self)):
			item = self[i]
			ret += '%s %.2f\r\n' % (str(item[0]), item[1])
		return ret

# DM指标
class DM(BaseInd):
	'''
	DM : 方向性移动运动指标(Directional Move Indicator),分为"正方向移动运动指标(DM+)"与"负方向移动运动指标(DM-)".
	最高价变化 : 当前最高价-先前最高价;
	最低价变化 : 先前最低价-当前最低价.
	
	若"最高价/最低价变化都<0"或“最高价/最低价变化相等”,则DM+与DM-都为0;
	若"最高价变化>最低价变化",则DM+为最高价变化,DM-为0;
	若"最高价变化<最低价变化",则DM+为0,DM-为最低价变化.
	'''
	def __init__(self):
		super(DM, self).__init__()
		self.__infos = [] # [0:时间,1:DM+数据,2:DM-数据]

	def __len__(self):
		return len(self.__infos)

	def __getitem__(self, key):
		if not isinstance(key, int):
			raise KeyError
		return self.__infos[key]

	@property
	def last(self):
		if len(self.__infos)<=0:
			return None
		item = self[-1]
		return (item[0], item[1], item[2])

	def update(self, scene):
		if len(scene)<2:
			return

		actual = -1
		prev = -2
		high_var = scene[actual].high-scene[prev].high
		low_var = scene[prev].low-scene[actual].low
		if high_var==low_var or \
			(high_var<0.0 and low_var<0.0):
			dm_plus = 0.0
			dm_minus = 0.0
		elif high_var>low_var:
			dm_plus = high_var
			dm_minus = 0.0
		else:
			dm_plus = 0.0
			dm_minus = low_var
		new_item = [scene[actual].time, dm_plus, dm_minus]
		self.__infos.append(new_item)

	def __str__(self):
		ret = ''
		for i in range(len(self)):
			item = self[i]
			ret += '%s %.2f %.2f\r\n' % (str(item[0]), item[1], item[2])
		return ret
 
# ADM指标
class ADM(BaseInd):
	'''
	指标DM的滑动平均
	'''
	def __init__(self, interval=10):
		super(ADM, self).__init__()
		self.__internal_dm = DM()
		self.__interval = interval
		self.__infos = [] # [0:时间,1:ADM+数据,2:ADM-数据]

	def __len__(self):
		return len(self.__infos)

	def __getitem__(self, key):
		if not isinstance(key, int):
			raise KeyError
		return self.__infos[key]
	
	@property
	def interval(self):
		return self.__interval

	@property
	def last(self):
		if len(self.__infos)<=0:
			return None
		item = self[-1]
		return (item[0], item[1], item[2])

	def update(self, scene):
		self.__internal_dm.update(scene)
		
		if len(self.__internal_dm)<self.interval:
			return

		prev = -2
		actual = -1
		
		result_plus = 0.0
		result_minus=  0.0
		if len(self)==0:
			# ADM+/ADM-第一次计算,取先前N个DM+/DM-的算术平均
			for i in range(self.interval):
				dm = self.__internal_dm[-i-1]
				result_plus += dm[1]
				result_minus += dm[2]
		else:
			result_plus += self.last[1]*(self.interval-1)+self.__internal_dm[actual][1]
			result_minus += self.last[2]*(self.interval-1)+self.__internal_dm[actual][2]
		result_plus /= self.interval
		result_minus /= self.interval

		new_item = [scene[actual].time, result_plus, result_minus]
		self.__infos.append(new_item)
	
	def __str__(self):
		ret = ''
		for i in range(len(self)):
			item = self[i]
			ret += '%s %.2f %.2f\r\n' % (str(item[0]), item[1], item[2])
		return ret

# TR指标
class TR(BaseInd):

	def __init__(self):
		super(TR, self).__init__()
		self.__infos = [] # [0:时间,1:TR数据]

	def __len__(self):
		return len(self.__infos)

	def __getitem__(self, key):
		if not isinstance(key, int):
			raise KeyError
		return self.__infos[key]

	@property
	def last(self):
		if len(self.__infos)<=0:
			return None
		item = self[-1]
		return (item[0], item[1])

	def update(self, scene):
		if len(scene)<2:
			return

		actual = -1
		prev =  -2
		val = math.fabs(scene[actual].high-scene[actual].low)
		val = max(val, math.fabs(scene[actual].high-scene[prev].close))
		val = max(val, math.fabs(scene[actual].low-scene[prev].close))
		new_item = [scene[actual].time, val]
		self.__infos.append(new_item)
	
	def __str__(self):
		ret = ''
		for i in range(len(self)):
			item = self[i]
			ret += '%s %.2f\r\n' % (str(item[0]), item[1])
		return ret

# ATR指标
class ATR(BaseInd):
	'''
	指标TR的滑动平均
	'''
	def __init__(self, interval=10):
		super(ATR, self).__init__()
		self.__internal_tr = TR()
		self.__interval = interval
		self.__infos = [] # [0:时间,1:ATR数据]

	def __len__(self):
		return len(self.__infos)

	def __getitem__(self, key):
		if not isinstance(key, int):
			raise KeyError
		return self.__infos[key]
	
	@property
	def interval(self):
		return self.__interval

	@property
	def last(self):
		if len(self.__infos)<=0:
			return None
		item = self[-1]
		return (item[0], item[1])

	def update(self, scene):
		self.__internal_tr.update(scene)
		
		if len(self.__internal_tr)<self.interval:
			return

		prev = -2
		actual = -1
		result = 0.0
		if len(self)==0:
			# ATR第一次计算,取先前N个TR的算术平均
			for i in range(self.interval):
				tr = self.__internal_tr[-i-1]
				result += tr[1]
		else:
			result += self.last[1]*(self.interval-1)+self.__internal_tr[actual][1]
		result /= self.interval

		new_item = [scene[actual].time, result]
		self.__infos.append(new_item)
	
	def __str__(self):
		ret = ''
		for i in range(len(self)):
			item = self[i]
			ret += '%s %.2f\r\n' % (str(item[0]), item[1])
		return ret

# DX指标
class DX(BaseInd):
	
	def __init__(self, interval=10):
		super(DX, self).__init__()
		self.__interval = interval
		self.__internal_adm = ADM(self.interval)
		self.__internal_atr = ATR(self.interval)
		self.__infos = [] # [0:时间,1:DX数据]

	def __len__(self):
		return len(self.__infos)

	def __getitem__(self, key):
		if not isinstance(key, int):
			raise KeyError
		return self.__infos[key]
	
	@property
	def interval(self):
		return self.__interval

	@property
	def last(self):
		if len(self.__infos)<=0:
			return None
		item = self[-1]
		return (item[0], item[1])

	def update(self, scene):
		self.__internal_adm.update(scene)
		self.__internal_atr.update(scene)

		if len(self.__internal_adm)<=0 or len(self.__internal_atr)<=0:
			return
		
		adm_plus = self.__internal_adm.last[1]
		adm_minus = self.__internal_adm.last[2]
		atr = self.__internal_atr.last[1]

		di_plus = round(adm_plus/atr*100.0)
		di_minus = round(adm_minus/atr*100.0)
		dx = round(math.fabs(di_plus-di_minus)/(di_plus+di_minus)*100.0)

		new_item = [scene.last.time, dx]
		self.__infos.append(new_item)

	def __str__(self):
		ret = ''
		for i in range(len(self)):
			item = self[i]
			ret += '%s %.2f\r\n' % (str(item[0]), item[1])
		return ret

# ADX指标
class ADX(BaseInd):
	'''
	ADX指标 : DX指标的滑动平均.
	用于衡量当前趋势的强弱,若大于一定值(一般40),则认为处于趋势中,若小于一定值(一般20),则认为处于盘整中.
	ADX的窗口宽度多取14. ---> 14代表"两周/半月",可尝试取"10/11".
	'''
	def __init__(self, interval=10):
		super(ADX, self).__init__()
		self.__interval = interval
		self.__internal_dx = DX(self.interval)
		self.__infos = [] # [0:时间,1:adx数据]
	
	def __len__(self):
		return len(self.__infos)

	def __getitem__(self, key):
		if not isinstance(key, int):
			raise KeyError
		return self.__infos[key]
	
	@property
	def interval(self):
		return self.__interval

	@property
	def last(self):
		if len(self.__infos)<=0:
			return None
		item = self[-1]
		return (item[0], item[1])

	def update(self, scene):
		self.__internal_dx.update(scene)
		
		if len(self.__internal_dx)<self.interval:
			return

		result = 0.0
		if len(self)==0:
			# ADX第一次计算,取先前N个DX的算术平均
			for i in range(self.interval):
				dx = self.__internal_dx[-i-1]
				result += dx[1]
		else:
			result += self.last[1]*(self.interval-1)+self.__internal_dx.last[1]
		result /= self.interval

		new_item = [scene.last.time, result]
		self.__infos.append(new_item)

	def __str__(self):
		ret = ''
		for i in range(len(self)):
			item = self[i]
			ret += '%s %.2f\r\n' % (str(item[0]), item[1])
		return ret

