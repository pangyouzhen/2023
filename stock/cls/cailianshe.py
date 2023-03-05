import datetime
import json
import re
import time
from typing import Optional

import requests
from bs4 import BeautifulSoup

from stock.utils.logger_utils import logger
from stock.utils.utils_ import parser_js
from stock.cls.stock_cls_alerts import stock_zh_a_alerts_cls


class Cls:
    def __init__(self, input_date: datetime.date, img_path, quick_info_path):
        self.headers = {
            'Host': 'www.cls.cn',
            'Connection': 'keep-alive',
            'Content-Length': '112',
            'Accept': 'application/json, text/plain, */*',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36',
            'Content-Type': 'application/json;charset=UTF-8',
            'Origin': 'https://www.cls.cn',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        # "2021-02-18"
        self.input_date: datetime.date = input_date
        self.today_cn = "%s月%s日" % (self.input_date.month, self.input_date.day)
        self.img_path = img_path
        self.quick_info_path = quick_info_path
        self.payload = "{\"type\":\"telegram\",\"keyword\":\"%s\",\"page\":0,\"rn\":20,\"os\":\"web\",\"sv\":\"7.2.2\",\"app\":\"CailianpressWeb\"}"
        self.url = "https://www.cls.cn/api/sw?app=CailianpressWeb&os=web"

    @logger.catch
    def get_schema_id(self) -> Optional[str]:
        schema_payload = self.payload % (self.today_cn + "涨停分析")
        print(schema_payload)
        response = requests.request("POST", self.url, headers=self.headers, data=schema_payload.encode("utf-8"))
        js = json.loads(response.text)
        data = js["data"]["telegram"]["data"]
        if len(data) > 0:
            schema = (data[0]["schema"])
            img_time_stamp = (data[0]["time"])
            schema_id = re.search("\d+", schema).group(0)
            if schema_id:
                if self.time_compare(img_time_stamp):
                    return schema_id
                else:
                    logger.warning("获取的时间戳过期")
            else:
                logger.warning("schema_id is None")
        else:
            logger.warning("获取data为空")

    @logger.catch
    def save_img(self, schema_id: str) -> None:
        url = "http://www.cls.cn/detail/%s" % schema_id
        response = requests.request("GET", url, headers=self.headers)
        page = response.text
        pagesoup = BeautifulSoup(page, 'lxml')
        links = [link for link in pagesoup.find_all(name='img', attrs={"src": re.compile(r'^https://img')})]
        if len(links) == 1:
            src_link = links[0].get("src")
            url = src_link.split("?")[0]
            html = requests.get(url)
            logger.info("开始保存文件")
            with open('%s/%s.png' % (self.img_path, self.input_date), 'wb') as file:
                file.write(html.content)
            logger.info("保存文件完成")
        else:
            logger.warning("没有所需链接")

    @logger.catch
    def quick_info(self):
        df = stock_zh_a_alerts_cls()
        df.to_csv("%s/qucik_%s.txt" % (self.quick_info_path, str(self.input_date)), encoding="utf-8")

    def cls_run(self) -> None:
        self.quick_info()
        schema_id = self.get_schema_id()
        if schema_id and self.input_date:
            self.save_img(schema_id)

    def time_compare(self, img_time_stamp: float):
        timestamp: float = time.mktime(self.input_date.timetuple())
        if img_time_stamp > timestamp:
            return True
        else:
            return False

# if __name__ == '__main__':
#     day = datetime.date(year=2021, month=3, day=23)
# cls = Cls(day, parent_path + "/project/stock/img", )
# print(cls.quick_info())
