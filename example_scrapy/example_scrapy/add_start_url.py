# -*- coding:utf-8 -*-
import redis

myredis = redis.Redis(host="192.168.0.86", password="root123456", port=6379)
print(myredis.info())
url = "https://www.dy2018.com/html/gndy/dyzz/index.html"
myredis.lpush("film_spider:start_urls", url)