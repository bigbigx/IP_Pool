def thread(need):
	with open("setting.json",'r',encoding='utf8') as setting_file:
		setting_dict = eval(setting_file.read())
		data = setting_dict[need]

	# Redis数据库地址
	data['REDIS_HOST'] = '127.0.0.1'

	# Redis端口
	data['REDIS_PORT'] = 6379

	# Redis密码，如无填None
	data['REDIS_PASSWORD'] = None

	REDIS_KEY = 'proxies'

	# 代理分数
	data['MAX_SCORE'] = 100
	data['MIN_SCORE'] = 0
	data['INITIAL_SCORE'] = 10

	data['VALID_STATUS_CODES'] = [200, 302]

	# 代理池数量界限
	data['POOL_UPPER_THRESHOLD'] = 50000

	# 检查周期
	data['TESTER_CYCLE'] = 20
	# 获取周期
	data['GETTER_CYCLE'] = 300

	# 测试API，建议抓哪个网站测哪个
	TEST_URL = ''

	# API配置
	data['API_HOST'] = '0.0.0.0'
	API_PORT = 5555

	# 开关
	data['TESTER_ENABLED'] = True
	data['GETTER_ENABLED'] = True
	data['API_ENABLED'] = True

	# 最大批测试量
	data['BATCH_TEST_SIZE'] = 10
	return data
