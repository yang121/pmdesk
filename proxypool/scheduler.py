import random
import time
from multiprocessing import Process

from pmdesk.settings import *
from .api import app
from .getter import Getter
from .tester import Tester


class Scheduler():
    def test_proxies(self, cycle=TESTER_CYCLE_RANGE):
        """
        定时测试代理
        """
        tester = Tester()
        while True:
            print('测试器开始运行')
            tester.run()
            time.sleep(random.randint(*cycle))

    def get_proxies(self, cycle=GETTER_CYCLE):
        """
        定时获取代理
        """
        getter = Getter()
        while True:
            print('开始抓取代理')
            getter.run()
            time.sleep(cycle)
    
    def run_api(self):
        """
        开启API
        """
        app.run(API_HOST, API_PORT)
    
    def run(self):
        print('代理池开始运行')
        
        if TESTER_ENABLED:
            tester_process = Process(target=self.test_proxies)
            tester_process.start()
        
        if GETTER_ENABLED:
            getter_process = Process(target=self.get_proxies)
            getter_process.start()
        
        if API_ENABLED:
            api_process = Process(target=self.run_api)
            api_process.start()
