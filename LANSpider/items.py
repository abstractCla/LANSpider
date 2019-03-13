# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join
from modules.ES_Type import NewsType
from w3lib.html import remove_tags
from elasticsearch_dsl.connections import connections
import re

# es = connections.create_connection(NewsType._doc_type.using)
es = connections.create_connection(hosts=["47.94.110.27"])


class LanspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class NewsItemLoader(ItemLoader):
    # 自定义ItemLoader
    default_output_processor = TakeFirst()


def gen_suggests(index, info_tuple):
    # 根据字符串生成搜索建议数组
    suggests = []
    for text, weight in info_tuple:
        # 调用ES Analyzer接口进行分词，大小写转换。
        if text:
            # {
            #     "tokens": [
            #         {
            #             "token": "洪荒",
            #             "start_offset": 0,
            #             "end_offset": 2,
            #             "type": "CN_WORD",
            #             "position": 0
            #         },
            #         {
            #             "token": "洪",
            #             "start_offset": 0,
            #             "end_offset": 1,
            #             "type": "CN_WORD",
            #             "position": 1
            #         },
            #         {
            #             "token": "荒",
            #             "start_offset": 1,
            #             "end_offset": 2,
            #             "type": "CN_WORD",
            #             "position": 2
            #         },
            #         {
            #             "token": "之力",
            #             "start_offset": 2,
            #             "end_offset": 4,
            #             "type": "CN_WORD",
            #             "position": 3
            #         },
            #         {
            #             "token": "之",
            #             "start_offset": 2,
            #             "end_offset": 3,
            #             "type": "CN_WORD",
            #             "position": 4
            #         },
            #         {
            #             "token": "力",
            #             "start_offset": 3,
            #             "end_offset": 4,
            #             "type": "CN_WORD",
            #             "position": 5
            #         }
            #     ]
            # }
            # words = es.indices.analyze(index=index, analyzer="ik_max_word", params={'filter': ["lowercase"]}, body=text)
            words = es.indices.analyze(index=index, body={"text": text, "analyzer": "ik_max_word"},
                                       params={"filter": ["lowercase"]})
            analyzed_words = set(word["token"] for word in words["tokens"] if len(word["token"]) > 1)
        else:
            analyzed_words = set()
        if analyzed_words:
            suggests.append({"input": list(analyzed_words), "weight": weight})
    return suggests


class XiDianNewsItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    date = scrapy.Field()
    source = scrapy.Field()
    click_num = scrapy.Field()
    content = scrapy.Field()

    def save_to_es(self):
        # 将Item转换为ES的数据
        news = NewsType()
        news.url = self['url']
        news.title = self['title']
        news.date = self['date']
        news.click_num = self['click_num']
        news.source = self['source']
        news.content = remove_tags(self['content'])
        # news.suggest = gen_suggests(NewsType._doc_type.index, (
        #     (re.sub('[^\w\s\u4e00-\u9fff]+', '', news.title), 10),
        #     (re.sub('[^\w\s\u4e00-\u9fff]+', '', news.source), 7)))
        news.suggest = gen_suggests(NewsType._doc_type.index, ((news.title, 10), (news.source, 7)))
        news.save()
        return
