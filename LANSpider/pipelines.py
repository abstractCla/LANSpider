# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class LanspiderPipeline(object):
    def process_item(self, item, spider):
        return item


class ElasticSearchPipeline(object):

    # 将数据写入到ES中
    def process_item(self, item, spider):
        # 将Item转换为ES的数据
        item.save_to_es()
        return item
