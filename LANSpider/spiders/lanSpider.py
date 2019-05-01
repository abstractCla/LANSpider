import scrapy
from scrapy.http import Request
from urllib import parse
from selenium import webdriver
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
import datetime
from LANSpider.items import XiDianNewsItem, NewsItemLoader
from pyvirtualdisplay import Display
from LANSpider.BloomFilter import PyBloomFilter
import mmh3
import redis
import math

pool = redis.ConnectionPool(host='127.0.0.1', port=6379, db=0)
conn = redis.StrictRedis(connection_pool=pool)
bf = PyBloomFilter(conn=conn)
class lanSpider(scrapy.Spider):  # 需要继承scrapy.Spider类，引入RedisSpider后是继承自RedisSpider

    name = "lanSpider"  # 定义蜘蛛名
    allowed_domains = ['news.xidian.edu.cn']

    # # 一种写法，无需定义start_requests方法
    # start_urls = ['https://news.xidian.edu.cn/yw.htm'] # 初始链接

    def __init__(self):
        # self.browser = webdriver.PhantomJS()
        display = Display(visible=0, size=(800, 600))
        display.start()
        self.browser = webdriver.Chrome()
        super(lanSpider, self).__init__()
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self, spider):
        # 当爬虫退出的时候关闭PhantomJS
        self.browser.quit()

    # 另外一种初始链接写法
    def start_requests(self):
        urls = [  # 爬取的链接由此方法通过下面链接爬取页面
            'https://news.xidian.edu.cn/yw.htm',
            'https://news.xidian.edu.cn/dt.htm',
            'https://news.xidian.edu.cn/mt.htm',
            'https://news.xidian.edu.cn/lljy.htm',
            'https://news.xidian.edu.cn/zjxz.htm',
            'https://news.xidian.edu.cn/xdms.htm',
            'https://news.xidian.edu.cn/kx.htm'
        ]
        for url in urls:
            yield Request(url=url, callback=self.parse)

    # 如果是简写初始url，此方法名必须为：parse

    def parse(self, response):
        post_nodes = response.css('.m-news-list .m-li-li')
        for post_node in post_nodes:
            display = post_node.css('::attr(style)').extract_first("")
            # if display == "display:none;":
            #     continue
            # else:
            post_url = post_node.css('::attr(href)').extract_first("")
            item_url = parse.urljoin(response.url, post_url)
            if not bf.is_exist(item_url):
                bf.add(item_url)
                yield Request(url=item_url, callback=self.parse_detail)

        next_url = response.css('.Next::attr(href)').extract_first("")
        if next_url:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    def parse_detail(self, response):
        # 实例化Items对象
        # news_item = XiDianNewsItem()
        # CSS方式
        title = response.css('.neirong-bt::text').extract_first("")
        date = response.css('#date::text').extract_first("")
        try:
            date = datetime.datetime.strptime(date, "发布时间：%Y-%m-%d %H:%M:%S").date()
        except Exception as e:
            date = datetime.datetime.now().date()
        source = response.css('#from::text').extract_first("").split('：')[1]
        click_num = response.css('#from span::text').extract_first("")
        paragraphs = response.css('.neirong .v_news_content p')
        content = ''
        for para in paragraphs:
            if para.css('img'):
                continue
            else:
                content = content + ''.join(para.css('::text').extract())
        # print(title, click_num, date, content)
        # 通过ItemLoader加载Item

        # 传送到pipelines中
        item = NewsItemLoader(item=XiDianNewsItem(), response=response)
        item.add_value("url", response.url)
        item.add_value("title", [title])
        item.add_value("date", [date])
        item.add_value("source", [source])
        item.add_value("click_num", [click_num])
        item.add_value("content", [content])
        news_item = item.load_item()
        # item.add_xpath()
        # item.add_value()
        yield news_item
