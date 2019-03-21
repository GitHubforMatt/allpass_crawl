# 基于Scrapy、Scrapy-redis、Scrapyd、Gerapy 的分布式爬虫框架

## 一、使用scrapy创建自己的爬虫项目

安装pip install scrapy
scrapy结构层级与运行生命周期在之前的内部分享中已经讲过，现不做赘述，直接再次演示示例项目。

### 创建项目：
cd到目标文件夹 
```
scrapy startproject example_scrapy
```

目标网站为电影天堂https://www.dy2018.com/html/gndy/dyzz/index.html
获取列表数据（分页），获取详情数据
![列表数据](/images/image1.png)
![分页](/images/image2.png)
![详情](/images/image3.png)

items.py文件中创建item类，类似常用的实体类：
```ruby
# 列表记录快照item
class snapshotItem(scrapy.Item):
    name = scrapy.Field()
    fullName = scrapy.Field()
    pageUrl = scrapy.Field()
    description = scrapy.Field()
    doubanRate = scrapy.Field()
    imdbRate = scrapy.Field()


# 详情item
class filmItem(scrapy.Item):
    name = scrapy.Field()
    enName = scrapy.Field()
    picUrl = scrapy.Field()
    fullName = scrapy.Field()
    details = scrapy.Field()
    downloadUrl = scrapy.Field()
    description = scrapy.Field()
    doubanRate = scrapy.Field()
    imdbRate = scrapy.Field()
    year = scrapy.Field()
```

cmd命令创建爬虫：
```
cd example_scrapy
scrapy genspider film_spider "www.dy2018.com"
```
或直接在spiders文件夹下手动添加。

编写film_spider.py
```ruby
# -*- coding: utf-8 -*-
import scrapy
from example_scrapy.items import snapshotItem,filmItem
from scrapy.http import Request

class FilmSpider(scrapy.Spider):
    # 爬虫名称
    name = 'film_spider'
    # 允许爬取域
    allowed_domains = ['www.dy2018.com']

    # 模拟headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
    }

    # 初始链接
    def start_requests(self):
        url = 'https://www.dy2018.com/html/gndy/dyzz/index.html'
        yield Request(url, headers=self.headers)

    # 默认request请求的回调函数
    def parse(self, response):
        # 解析列表、分页
        links=response.xpath('//div//table//td/b/a')
        nexts=response.xpath('//div[@class="x"]/a/@href').extract()

        for nextpage in nexts:
            yield Request(url="https://www.dy2018.com"+nextpage,callback=self.parse)

        # 分页实体
        item=snapshotItem()
        for link in links:
            item['pageUrl']=link.css("a::attr('href')").extract_first().encode('utf8').decode()
            # 请求详情页
            yield Request(url="https://www.dy2018.com"+str(item['pageUrl']),callback=self.parseDetail)
            item['name']=link.xpath('text()').extract_first().encode('utf8').decode()
            # 输出列表记录
            yield item

    # 获取详情item
    def parseDetail(self,response):
        film=filmItem()
        film['name']=response.xpath('//div[@class="title_all"]//h1//text()').get()
        film['picUrl']=response.xpath('//div[@id="Zoom"]//p//img//@src').extract()
        film['downloadUrl']=response.xpath('//div[@id="Zoom"]//a//@href').extract()
        film['details']=response.xpath('//div[@id="Zoom"]//p//text()').extract()
        # 输出详情记录
        yield film
```
settings.py中添加mongodb连接配置
```
# mongodb settings
MONGO_HOST='mongodb://127.0.0.1:27017/'
MONGO_DB="films"
SNAPSHOT_COLL='snapshots'
FILM_COLL='details'
```
pipeline管道接收item保存mongodb，pipelines.py创建连接以及保存：
```ruby
# -*- coding: utf-8 -*-
from scrapy.conf import settings
import pymongo
from example_scrapy.items import filmItem,snapshotItem
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class ExampleScrapyPipeline(object):
    def __init__(self):
        # 创建mongodb链接
        self.snapshot_coll=pymongo.MongoClient(host=settings['MONGO_HOST'])[settings['MONGO_DB']][settings['SNAPSHOT_COLL']]
        self.film_coll=pymongo.MongoClient(host=settings['MONGO_HOST'])[settings['MONGO_DB']][settings['FILM_COLL']]

    # 管道接收item实体保存数据库
    def process_item(self, item, spider):

        if type(item)==snapshotItem:
            # 列表记录item
            snapshot_item=dict(name=item['name'],pageUrl=item['pageUrl'])
            self.snapshot_coll.insert(snapshot_item)
        elif type(item)==filmItem:
            # 详情记录item
            film_item=dict(name=item['name'],picUrl=item['picUrl'],downloadUrl=item['downloadUrl'],details=item['details'])
            self.film_coll.insert(film_item)
        return item
```

settings.py中添加配置启用管道
```
ITEM_PIPELINES = {
   'example_scrapy.pipelines.ExampleScrapyPipeline': 300,
}
```
到此为止，一个简单的爬虫就写完了，可在settings.py的同级目录下创建main.py开启爬虫
```ruby
# -*- coding: utf-8 -*-
from scrapy.cmdline import execute

execute(['scrapy', 'crawl', 'film_spider'])
```

### 使用scrapy-redis调度爬虫
如果爬取的目标数据体量很大，单台机器爬取速度太慢，想分布式爬取如何操作？很简单，接下介绍如何将example_scrapy这个示例修改为可分布式部署的爬虫。
安装scrapy-redis
```
pip install scrapy-redis
```

1.settings.py中添加redis连接配置、使用scrapy_redis调度器配置、scrapy_redis自带去重配置、启用scrapy_redis管道
```
# Specify the host and port to use when connecting to Redis (optional).
REDIS_HOST = '192.168.0.86'
REDIS_PORT = 6379
REDIS_PASSWORD = 'root123456'
REDIS_URL = 'redis://:root123456@192.168.0.86:6379'

# Enables scheduling storing requests queue in redis.
SCHEDULER = "scrapy_redis.scheduler.Scheduler"

# Ensure all spiders share same duplicates filter through redis.
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"

ITEM_PIPELINES = {
   'dygod.pipelines.DygodPipeline': 300,
   'scrapy_redis.pipelines.RedisPipeline': 400,#数字代表先后执行顺序
}
```

2.film_spider.py中添加scrapy_redis.spiders引用，导入RedisSpider，修改FilmSpider类继承RedisSpider，去掉原有的def start_requests(self)初始链接方法，改为redis_key = 'film_spider:start_urls'（scrapy-redis分布式爬虫中是依赖spider中设置的redis_key启动,redis_key为固定语法）,其他代码不需要修改。
```javascript {highlight=[5,18-22]}
# -*- coding: utf-8 -*-
import scrapy
from example_scrapy.items import snapshotItem,filmItem
from scrapy.http import Request
from scrapy_redis.spiders import RedisSpider

class FilmSpider(RedisSpider):
    # 爬虫名称
    name = 'film_spider'
    # 允许爬取域，可以去掉
    allowed_domains = ['www.dy2018.com']

    # 模拟headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
    }

    redis_key = 'film_spider:start_urls'
    # 初始链接
    # def start_requests(self):
    #     url = 'https://www.dy2018.com/html/gndy/dyzz/index.html'
    #     yield Request(url, headers=self.headers)

    # 默认request请求的回调函数
    def parse(self, response):
```
至此，example_scrapy的分布式修改已经结束，运行main.py,向redis中push初始链接的key-value：
1.redis-cli连接redis服务去输⼊push指令
```
redis> lpush film_spider:start_urls https://www.dy2018.com/html/gndy/dyzz/index.html
```
2.新建add_start_url.py文件向redis添加初始连接
```ruby
# -*- coding:utf-8 -*-
import redis

myredis = redis.Redis(host="192.168.0.86", password="root123456", port=6379)
print(myredis.info())
url = "https://www.dy2018.com/html/gndy/dyzz/index.html"
myredis.lpush("film_spider:start_urls", url)
```
运行结果：
![运行输出](/images/image4.png)
![mongodb数据](/images/image5.png)

#### 使用代理
频繁请求ip被封了怎么办？来个代理中间就好了。middlewares.py中添加代码（此处以我本地动态代理池为例）
settings.py中添加动态、静态代理ip池配置
```
# 静态固定代理，示例使用，不稳定，可替换为自己的固定稳定代理
IPPOOL=[
    {"ipaddr":"222.162.13.227:80"},
    {"ipaddr":"42.228.3.158:8080"},
    {"ipaddr":"39.137.69.7:8080"},
    {"ipaddr":"115.159.31.195:8080"},
    {"ipaddr":"119.28.203.242:8000"},
    {"ipaddr":"136.228.128.164:46458"},
    {"ipaddr":"119.28.203.242:8000"}
]

# 动态代理获取地址
PROXY_POOL_URL = 'http://192.168.0.86:5010/get'
```

```ruby
# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import requests
from scrapy.conf import settings
import random


class HttpbinProxyMiddleware(object):

    def process_request(self, request, spider):
        # 获取动态代理地址
        proxy_pool_url=settings['PROXY_POOL_URL']
        pro_addr = requests.get(proxy_pool_url).text
        print("当前使用动态代理IP是："+pro_addr)
        request.meta['proxy'] = 'http://' + pro_addr

        # 获取静态代理ip
        # ip=random.choice(settings['IPPOOL'])
        # print("当前使用静态代理IP是：" + ip)
        # request.meta['proxy'] = 'http://' + ip
```

settings.py中开启配置使用代理中间件
```
DOWNLOADER_MIDDLEWARES = {
   'httpbin.middlewares.HttpbinProxyMiddleware': 543,
}
```
以上面同样的方式启动爬虫，代理成功
![代理成功](/images/image6.png)

分布式爬虫已经写好，如何发布部署统一调度呢？接下来介绍Gerapy，一个基于Scrapyd，Scrapyd API，Django，Vue.js搭建的分布式爬虫管理框架，目前版本文档先不讲解Gerapy的源码和部署配置，仅介绍基本界面使用操作和讲解Scrapyd安装。


## 二、Scrapyd简介安装
Scrapyd是一个用来部署和运行Scrapy项目的应用。其可以通过一个简单的Json API来部署（上传）或者控制Scrapy项目。
Scrapyd可以用来管理多个项目，并且每个项目还可以上传多个版本，不过只有最新的版本会被使用。
在安装并开启Scrapyd之后，它将会挂起一个服务来监听运行爬虫的请求，并且根据请求为每一个爬虫启用一个进程来运行。Scrapyd同样支持同时运行多个进程，进程的数量由max_proc和max_proc_per_cpu选项来限制。

nodes子节点安装Scrapyd：
1.pip install scrapyd（需安装python3、scrapy、twisted等一系列包较麻烦），安装成功后cd到任意存储文件夹，执行scrapyd开启服务
2.安装docker直接pull私有仓库
vim或gedit创建/修改 /etc/docker/daemon.json 为
{ "insecure-registries":["192.168.0.196:8003"] }
docker pull 192.168.0.196:8003/xuzhe_scrapyd:v1 后直接，
开启Scrapyd服务：$ scrapyd

Scrapyd配置文件路径：
/etc/scrapyd/scrapyd.conf (Unix)
'python安装路径'\Lib\site-packages\scrapyd\default_scrapyd.conf (Windows)

主要配置介绍例：
```ruby
[scrapyd]
eggs_dir    = eggs  #存储工程egg文件的目录
logs_dir    = logs  #存储Scrapy日志的目录，不存储日志logs_dir =
items_dir   =       #存储items的目录，一般不需要设置这个选项，因为抓取下来的数据都会存到数据库中。
jobs_to_keep = 5    #每个spider保留多少个完成的job，默认为5
dbs_dir     = dbs   #项目存储数据库的目录，也包括爬虫队列
max_proc    = 0     #同时启动的最大Scrapy进程数，如果没有设置或者设置为0，那么将会使用当前cpu可用的核数乘以max_proc_per_cpu的值。默认为0。
max_proc_per_cpu = 4    #每个cpu能同时启动的最大Scrapy进程数。默认为4。
finished_to_keep = 100  #启动器中保留的已完成进程的数量，默认为100
poll_interval = 5.0     #轮询队列的间隔，以秒为单位，默认值为5
bind_address = 0.0.0.0   #网页和Json服务监听的IP地址，默认为127.0.0.1，改为0.0.0.0可远程连接
http_port   = 6800   #API监听的端口，默认为6800
debug       = off    #是否开启debug模式
runner      = scrapyd.runner     #用来启动子进程的启动器，可以自定义启动的模块
application = scrapyd.app.application
launcher    = scrapyd.launcher.Launcher
webroot     = scrapyd.website.Root

[services]
schedule.json     = scrapyd.webservice.Schedule
cancel.json       = scrapyd.webservice.Cancel
addversion.json   = scrapyd.webservice.AddVersion
listprojects.json = scrapyd.webservice.ListProjects
listversions.json = scrapyd.webservice.ListVersions
listspiders.json  = scrapyd.webservice.ListSpiders
delproject.json   = scrapyd.webservice.DeleteProject
delversion.json   = scrapyd.webservice.DeleteVersion
listjobs.json     = scrapyd.webservice.ListJobs
daemonstatus.json = scrapyd.webservice.DaemonStatus
```
直接调用scrapyd接口部署、调度scrapy项目这方面暂时不做说明，我们直接使用gerapy可视化操作scrapyd。

## 三、在master机上使用Gerapy统一管理爬虫项目
打开已经配置好Gerapy的master主机 http://192.168.0.86:8000/#/home
可切换中文显示
![切换中文](/images/image7.png)

在主机管理中添加scrapyd运行的地址和端口，如下：
![主机列表](/images/image8.png)
![添加主机](/images/image9.png)

连接192.168.0.86主机共享盘\\\192.168.0.86\gerapy_demo\gerapy,将你写好的scrapy项目放入master机的projects文件夹，**拷贝之前务必将项目主文件下scrapy.cfg文件中 [deploy]下url配置打开注释**

```javascript {highlight=10}
# Automatically created by: scrapy startproject
#
# For more information about the [deploy] section see:
# https://scrapyd.readthedocs.org/en/latest/deploy.html

[settings]
default = example_scrapy.settings

[deploy]
url = http://localhost:6800/
project = example_scrapy
```
![拷贝项目](/images/image10.png)
![拷贝项目](/images/image11.png)

可以点击上图中的编辑，在线编辑项目（应急使用，有bug后续版本优化），如果项目没有问题，可以点击部署进行打包和部署，在部署之前要打包项目（打包成一个egg文件），可以部署到多台主机。
![打包](/images/image12.png)
![部署](/images/image13.png)

回到主机管理选择刚才部署的主机，进行调度运行爬虫
![调度](/images/image14.png)
![运行](/images/image15.png)
爬虫运行输出日志
![输出日志](/images/image16.png)

