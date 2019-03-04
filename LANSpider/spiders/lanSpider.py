import scrapy
from scrapy.http import Request
from urllib import parse
from selenium import webdriver
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
import datetime

class lanSpider(scrapy.Spider):  # 需要继承scrapy.Spider类

    name = "lanSpider"  # 定义蜘蛛名
    allowed_domains = ['news.xidian.edu.cn']
    # # 一种写法，无需定义start_requests方法
    # start_urls = ['https://news.xidian.edu.cn/yw.htm'] # 初始链接

    def __init__(self):
        self.browser = webdriver.PhantomJS()
        super(lanSpider, self).__init__()
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self, spider):
        # 当爬虫退出的时候关闭PhantomJS
        self.browser.quit()

    # 另外一种初始链接写法
    def start_requests(self):
        urls = [  # 爬取的链接由此方法通过下面链接爬取页面
            # 'https://news.xidian.edu.cn/yw.htm',
            'https://news.xidian.edu.cn/info/1371/202795.htm',
        ]
        for url in urls:
            yield Request(url=url, callback=self.parse)

    # 如果是简写初始url，此方法名必须为：parse

    def parse_bak(self, response):
        post_nodes = response.css('.m-news-list .m-li-li')
        for post_node in post_nodes:
            display = post_node.css('::attr(style)').extract_first("")
            if display == "display:none;":
                continue
            else:
                title = post_node.css('.pc-news-li .pc-news-bt::text').extract_first("")
                click_num = post_node.css('.pc-news-li .pc-news-dj span::text').extract_first("")
                time = post_node.css('.pc-news-sj::text').extract_first("")
                try:
                    time = datetime.datetime.strptime(time, "%Y-%m-%d").date()
                except Exception as e:
                    time = datetime.datetime.now().date()
                source = post_node.css('.pc-news-ly::text').extract_first("").split('：')[1]
                post_url = post_node.css('::attr(href)').extract_first("")
                yield scrapy.Request(url=parse.urljoin(response.url, post_url),callback=self.parse_detail)
                print(title, click_num, post_url, time, source, parse.urljoin(response.url, post_url))

        next_url = response.css('.Next::attr(href)').extract_first("")
        if next_url:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    def parse(self, response):
        # 实例化Items对象
        # article_items = JobBoleArticleItem()
        # CSS方式
        paragraphs = response.css('.neirong .v_news_content p')
        content = ''
        for para in paragraphs:
            if para.css('img'):
                continue
            else:
                content = content+''.join(para.css('::text').extract())
        print(content)
        #
        # article_items["title"] = title_css
        # article_items["url"] = response.url
        # article_items["url_obj_id"] = get_md5(article_items["url"])
        # article_items["create_date"] = time_css
        # article_items["front_image_url"] = [front_image_url]
        # # article_items["front_image_path"] =
        # article_items["like_nums"] = like_nums_css
        # article_items["collect_nums"] = collect_nums_css
        # article_items["comment_nums"] = comment_nums_css
        # article_items["tags"] = tags_css
        # article_items["content"] = content_css
        #
        # # 通过ItemLoader加载Item
        #
        # # 传送到pipelines中
        # item = ArticleItemLoader(item=JobBoleArticleItem(), response=response)
        # item.add_css("title", '.entry-header h1::text')
        # item.add_value("url", response.url)
        # item.add_value("url_obj_id", get_md5(article_items["url"]))
        # item.add_css("create_date", '.entry-meta-hide-on-mobile::text')
        # item.add_value("front_image_url", [front_image_url])
        # item.add_css("like_nums", '.vote-post-up h10::text')
        # item.add_css("collect_nums", '.bookmark-btn::text')
        # item.add_css("comment_nums", 'a[href="#article-comment"] span::text')
        # item.add_css("tags", 'p.entry-meta-hide-on-mobile a::text')
        # item.add_css("content", 'div.entry')
        # article_items = item.load_item()
        # # item.add_xpath()
        # # item.add_value()
        # yield article_items