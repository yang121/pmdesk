import os

BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Redis数据库地址
REDIS_HOST = '127.0.0.1'

# Redis端口
REDIS_PORT = 6379

# Redis密码，如无填None
REDIS_PASSWORD = None

REDIS_KEY = 'proxies'

# 代理分数
MAX_SCORE = 10
MIN_SCORE = 0
INITIAL_SCORE = 5

VALID_STATUS_CODES = [200, 302]

# 代理池数量界限
POOL_UPPER_THRESHOLD = 100

# 检查周期(随机范围)
TESTER_CYCLE_RANGE = 20, 100
# 获取周期
GETTER_CYCLE = 300

# 测试API，建议抓哪个网站测哪个
TEST_URL = 'http://shouji.baidu.com/'

# API配置
API_HOST = '0.0.0.0'
API_PORT = 5555

# 开关
TESTER_ENABLED = True
GETTER_ENABLED = True
API_ENABLED = True

# 最大批测试量(自动随机分批)
BATCH_TEST_SIZE = 10


DEBUG = False
PAGE_RANGE = 501, 510

MONGO_URL = 'localhost'
MONGO_DB = 'papa'
MONGO_TABLE = 'app_name'

PROXY_MODE = True
PROXY_GET_URL = 'http://0.0.0.0:5555/random'

BASE_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
    'Connection': 'close'
}