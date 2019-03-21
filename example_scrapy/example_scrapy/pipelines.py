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
