import asyncio
import aiohttp
import time
import sys

try:
    from aiohttp import ClientError
except:
    from aiohttp import ClientProxyConnectionError as ProxyConnectionError
from proxypool.db import RedisClient



class Tester(object):
    def __init__(self,data):
        self.redis = RedisClient(data)
        self.data = data

    async def test_single_proxy(self, proxy):
        """
        测试单个代理
        :param proxy:
        :return:
        """
        conn = aiohttp.TCPConnector(verify_ssl=False)
        async with aiohttp.ClientSession(connector=conn) as session:
            try:
                if isinstance(proxy, bytes):
                    proxy = proxy.decode('utf-8')
                real_proxy = 'http://' + proxy
                print('正在测试', proxy)
                async with session.get(self.data['TEST_URL'], proxy=real_proxy, timeout=15, allow_redirects=False) as response:
                    text =  await response.read()
                    if self.data['TEST_tage'] == 'in':
                        if bytes(self.data['TEST_if'], encoding="utf8") in text:
                            self.redis.max(proxy)
                            print('代理可用', proxy)
                        else:
                            self.redis.decrease(proxy)
                            print('不满足条件{}'.format(self.data['TEST_if']+self.data['TEST_tage'] ), response.status, 'IP', proxy)
                    if self.data['TEST_tage'] == 'not in':
                        if bytes(self.data['TEST_if'], encoding="utf8") not in text:
                            self.redis.max(proxy)
                            print('代理可用', proxy)
                        else:
                            self.redis.decrease(proxy)
                            print('不满足条件{}'.format(self.data['TEST_if'] + self.data['TEST_tage']), response.status, 'IP', proxy)
            except (ClientError, aiohttp.client_exceptions.ClientConnectorError, asyncio.TimeoutError, AttributeError):
                self.redis.delete(proxy)
                print('代理请求失败', proxy)

    async def _single_proxy(self, proxy):
        """
        测试单个代理
        :param proxy:
        :return:
        """


    def run(self):
        """
        测试主函数
        :return:
        """
        print('测试器开始运行')
        try:
            count = self.redis.count()
            print('当前剩余', count, '个代理')
            for i in range(0, count, self.data['BATCH_TEST_SIZE']):
                start = i
                stop = min(i + self.data['BATCH_TEST_SIZE'], count)
                print('正在测试第', start + 1, '-', stop, '个代理')
                test_proxies = self.redis.batch(start, stop)
                loop = asyncio.get_event_loop()
                tasks = [self.test_single_proxy(proxy) for proxy in test_proxies]
                loop.run_until_complete(asyncio.wait(tasks))
                sys.stdout.flush()
                time.sleep(5)
        except Exception as e:
            print('测试器发生错误', e.args)

# Tester().run()