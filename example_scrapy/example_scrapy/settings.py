# -*- coding: utf-8 -*-

# Scrapy settings for example_scrapy project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'example_scrapy'

SPIDER_MODULES = ['example_scrapy.spiders']
NEWSPIDER_MODULE = 'example_scrapy.spiders'

# mongodb settings
MONGO_HOST='mongodb://127.0.0.1:27017/'
MONGO_DB="films1"
SNAPSHOT_COLL='snapshots1'
FILM_COLL='details1'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'example_scrapy (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'example_scrapy.middlewares.ExampleScrapySpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
   'example_scrapy.middlewares.HttpbinProxyMiddleware': 543,
}

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

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'example_scrapy.pipelines.ExampleScrapyPipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# Enables scheduling storing requests queue in redis.
SCHEDULER = "scrapy_redis.scheduler.Scheduler"

# Ensure all spiders share same duplicates filter through redis.
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"

# Specify the host and port to use when connecting to Redis (optional).
REDIS_HOST = '192.168.0.86'
REDIS_PORT = 6379
REDIS_PASSWORD = 'root123456'
REDIS_URL = 'redis://:root123456@192.168.0.86:6379'