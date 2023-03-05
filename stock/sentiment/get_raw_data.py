# 获取原始的数据，并将原始数据进行保存，需要根据交易日进行运行
import datetime

import akshare as ak

from stock.utils.logger_utils import logger


class RawData:
    def __init__(self, input_date: datetime.date, path: str):
        self.path = path
        self.input_date_str = str(input_date)

    @logger.catch
    def get_raw_data(self):
        stock_zh_a_spot_df = ak.stock_zh_a_spot()
        stock_zh_a_spot_df.to_csv(self.path + "/%s.csv" % self.input_date_str, index=False, encoding="utf-8")
