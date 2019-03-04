from scrapy.cmdline import execute

import sys
import os

#获取当前文件的所在文件夹目录
#print(os.path.dirname(os.path.abspath(__file__)))

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
execute(["scrapy", "crawl", "lanSpider"])