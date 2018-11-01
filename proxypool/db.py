import redis
from proxypool.error import PoolEmptyError
from random import choice
import re


class RedisClient(object):
    def __init__(self, data,):
        """
        初始化
        :param host: Redis 地址
        :param port: Redis 端口
        :param password: Redis密码
        """
        self.data = data
        self.REDIS_HOST = '127.0.0.1' if self.data.get('REDIS_HOST') == None else self.data['REDIS_HOST']
        self.REDIS_PORT = 6379 if self.data.get('REDIS_PORT') == None else self.data['REDIS_PORT']
        self.REDIS_PASSWORD = None if self.data.get('REDIS_PASSWORD') == None else self.data['REDIS_PASSWORD']
        self.REDIS_KEY = self.data['REDIS_KEY']
        self.MAX_SCORE = 100 if self.data.get('MAX_SCORE') == None else self.data['MAX_SCORE']
        self.MIN_SCORE = 0 if self.data.get('MIN_SCORE') == None else self.data['MIN_SCORE']
        self.INITIAL_SCORE = 10 if self.data.get('INITIAL_SCORE') == None else self.data['INITIAL_SCORE']

        host = self.REDIS_HOST
        port = self.REDIS_PORT
        password = self.REDIS_PASSWORD
        self.db = redis.StrictRedis(host=host, port=port, password=password, decode_responses=True)
    
    def add(self, proxy,score=1):
        """
        添加代理，设置分数为最高
        :param proxy: 代理
        :param score: 分数
        :return: 添加结果
        """
        score = self.INITIAL_SCORE
        if not re.match('\d+\.\d+\.\d+\.\d+\:\d+', proxy):
            print('代理不符合规范', proxy, '丢弃')
            return
        if not self.db.zscore(self.REDIS_KEY, proxy):
            return self.db.zadd(self.REDIS_KEY, score, proxy)
    
    def random(self):
        """
        随机获取有效代理，首先尝试获取最高分数代理，如果不存在，按照排名获取，否则异常
        :return: 随机代理
        """
        result = self.db.zrangebyscore(self.REDIS_KEY, self.MAX_SCORE, self.MAX_SCORE)
        if len(result):
            return choice(result)
        else:
            result = self.db.zrevrange(self.REDIS_KEY, 0, 100)
            if len(result):
                return choice(result)
            else:
                raise PoolEmptyError
    
    def decrease(self, proxy):
        """
        代理值减一分，小于最小值则删除
        :param proxy: 代理
        :return: 修改后的代理分数
        """
        score = self.db.zscore(self.REDIS_KEY, proxy)
        if score and score > self.MIN_SCORE:
            print('代理', proxy, '当前分数', score, '减1')
            return self.db.zincrby(self.REDIS_KEY, proxy, -1)
        else:
            print('代理', proxy, '当前分数', score, '移除')
            return self.db.zrem(self.REDIS_KEY, proxy)

    def delete(self,proxy):
        score = self.db.zscore(self.REDIS_KEY, proxy)
        print('代理', proxy, '当前分数', score, '因为请求失败移除')
        return self.db.zrem(self.REDIS_KEY, proxy)

    def exists(self, proxy):
        """
        判断是否存在
        :param proxy: 代理
        :return: 是否存在
        """
        return not self.db.zscore(self.REDIS_KEY, proxy) == None
    
    def max(self, proxy):
        """
        将代理设置为MAX_SCORE
        :param proxy: 代理
        :return: 设置结果
        """
        print('代理', proxy, '可用，设置为', self.MAX_SCORE)
        return self.db.zadd(self.REDIS_KEY, self.MAX_SCORE, proxy)
    
    def count(self):
        """
        获取数量
        :return: 数量
        """
        return self.db.zcard(self.REDIS_KEY)
    
    def all(self):
        """
        获取全部代理
        :return: 全部代理列表
        """
        return self.db.zrangebyscore(self.REDIS_KEY, self.MIN_SCORE, self.MAX_SCORE)
    
    def batch(self, start, stop):
        """
        批量获取
        :param start: 开始索引
        :param stop: 结束索引
        :return: 代理列表
        """
        return self.db.zrevrange(self.REDIS_KEY, start, stop - 1)


# if __name__ == '__main__':
#     conn = RedisClient()
#     result = conn.batch(680, 688)
#     print(result)
