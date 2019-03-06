from datetime import datetime
from elasticsearch_dsl import DocType, Date, Nested, Boolean, \
    analyzer, Completion, Keyword, Text, Integer
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer

# 链接数据库
connections.create_connection(hosts=["localhost"])

class CustomAnalyzer(_CustomAnalyzer):
    def get_analysis_definition(self):
        return {}


ik_analyzer = CustomAnalyzer("ik_max_word", filter=["lowercase"])


class NewsType(DocType):
    # 西电新闻类型
    # suggest = Completion(analyzer=ik_analyzer)

    url = Keyword()
    title = Text(analyzer="ik_max_word") # String分为Text 和 Keyword, Text需被分词检索，Keyword需完全匹配
    date = Date()
    click_num = Integer()
    source = Text(analyzer="ik_max_word")
    content = Text(analyzer="ik_max_word")

    # 确定index和type
    class Meta:
        index = "XiDian"
        doc_type = "news"


if __name__ == "__main__":
    NewsType.init()

