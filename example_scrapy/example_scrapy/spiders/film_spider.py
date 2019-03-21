# -*- coding: utf-8 -*-
import scrapy
from example_scrapy.items import snapshotItem,filmItem
from scrapy.http import Request
from scrapy_redis.spiders import RedisSpider

class FilmSpider(RedisSpider):
    # 爬虫名称
    name = 'film_spider'

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
        print(response.text)
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