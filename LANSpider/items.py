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

# es = connections.create_connection(NewsType._doc_type.usinig)
class LanspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class NewsItemLoader(ItemLoader):
    # 自定义ItemLoader
    default_output_processor = TakeFirst()


class XiDianNewsItem(scrapy.Item):
    class JobBoleArticleItem(scrapy.Item):
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
        # news.suggest = gen_suggests(ArticleType._doc_type.index, ((article.title, 10), (article.tags, 7)))
        news.save()
        return
