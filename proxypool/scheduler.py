import time
from multiprocessing import Process
from proxypool.api import app
from proxypool.getter import Getter
from proxypool.tester import Tester
from proxypool.db import RedisClient
from flask import Flask, g

from .db import RedisClient


class Scheduler():
    def __init__(self,data):
        self.data = data
    def schedule_tester(self,cycle=1):
        """
        定时测试代理
        """
        tester = Tester(self.data)
        cycle = self.data['TESTER_CYCLE']
        while True:
            print('测试器开始运行')
            tester.run()
            time.sleep(cycle)
    
    def schedule_getter(self, cycle=1):
        """
        定时获取代理
        """
        cycle = self.data['GETTER_CYCLE']
        getter = Getter(self.data)
        while True:
            print('开始抓取代理')
            getter.run()
            time.sleep(cycle)
    
    def schedule_api(self):
        """
        开启API
        """
        app = Flask(__name__)

        def get_conn(data):
            if not hasattr(g, 'redis'):
                g.redis = RedisClient(data)
            return g.redis

        @app.route('/')
        def index():
            return '<h2>Welcome to Proxy Pool System</h2>'

        @app.route('/random')
        def get_proxy():
            """
            Get a proxy
            :return: 随机代理
            """
            conn = get_conn(self.data)
            return conn.random()

        @app.route('/count')
        def get_counts(data):
            """
            Get the count of proxies
            :return: 代理池总量
            """
            conn = get_conn(self.data)
            return str(conn.count())
        app.run(self.data['API_HOST'], self.data['API_PORT'])

    def run(self):
        print('代理池开始运行')
        
        if self.data['TESTER_ENABLED']:
            tester_process = Process(target=self.schedule_tester)
            tester_process.start()
        
        if self.data['GETTER_ENABLED']:
            getter_process = Process(target=self.schedule_getter)
            getter_process.start()
        
        if self.data['API_ENABLED']:
            api_process = Process(target=self.schedule_api)
            api_process.start()
