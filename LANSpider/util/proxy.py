import requests
import MySQLdb
from fake_useragent import UserAgent
from scrapy.selector import Selector

conn = MySQLdb.connect('localhost', 'LANSpider', 'zhumingliang,', 'spider', charset='utf8', use_unicode=True)
cursor = conn.cursor()


def crawl_proxy():
    # 爬取快代理的免费高匿IP
    ua = UserAgent(verify_ssl=False)
    # ua.update()
    agent = ua.random
    headers = {
        'User-Agent': agent,
    }
    for i in range(1, 1000):
        re = requests.get('https://www.kuaidaili.com/free/inha/{0}/'.format(i), headers=headers)
        selector = Selector(text=re.text)
        all_trs = selector.css("#list table tbody tr")
        ip_list = []
        for tr in all_trs:
            ip = tr.css('[data-title="IP"]::text').extract_first("")
            port = tr.css('[data-title="PORT"]::text').extract_first("")
            proxy_type = tr.css('[data-title="类型"]::text').extract_first("")
            speed_str = tr.css('[data-title="响应速度"]::text').extract_first("")
            if speed_str:
                try:
                    speed = float(speed_str.strip("秒")[0])
                except:
                    speed = 0.0
            ip_list.append((ip, port, proxy_type, speed))
        for ip_li in ip_list:
            cursor.execute(
                "insert into proxy(ip, port, proxy_type, speed) VALUES ('{0}', '{1}', '{2}', {3})".format(ip_li[0],
                                                                                                          ip_li[1],
                                                                                                          ip_li[2],
                                                                                                          ip_li[3]))
        conn.commit()
        print('第%d次爬取完成' % i)


class GetIP(object):
    def delete_ip(self, ip):
        # 从数据库中删除无效的ip
        delete_sql = """
            delete from proxy where ip='{0}'
        """.format(ip)
        cursor.execute(delete_sql)
        conn.commit()
        return True

    def judge_ip(self, ip, port):
        # 判断ip是否可用
        http_url = "https://news.xidian.edu.cn/"
        proxy_url = "http://{0}:{1}".format(ip, port)
        try:
            proxy_dict = {
                "http": proxy_url,
            }
            response = requests.get(http_url, proxies=proxy_dict)
        except Exception as e:
            print("Invalid ip and port.")
            self.delete_ip(ip)
            return False
        else:
            code = response.status_code
            if code >= 200 and code < 300:
                print("Effective ip and port.")
                return True
            else:
                print("Invalid ip and port.")
                self.delete_ip(ip)
                return False

    def get_random_ip(self):
        # 从数据库中随机获取一个可用的ip
        random_sql = """
            SELECT ip, port FROM proxy
            ORDER BY RAND()
            LIMIT 1
            """
        result = cursor.execute(random_sql)
        for ip_info in cursor.fetchall():
            ip = ip_info[0]
            port = ip_info[1]
            judge_re = self.judge_ip(ip, port)
            if judge_re:
                return "http://{0}:{1}".format(ip, port)
            else:
                return self.get_random_ip()


# crawl_ips()

if __name__ == "__main__":
    ip = GetIP()
    random_ip = ip.get_random_ip()
    print(random_ip)
    # crawl_proxy()
