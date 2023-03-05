import datetime
from typing import List, Tuple

import pandas as pd
import time


class DateUtils:
    def __init__(self, path: str = None, input_date: datetime.date = None):
        """
        input_date: "2021-03-10"
        """
        if input_date:
            self.input_date: datetime.date = input_date
        else:
            self.input_date: datetime.date = datetime.date.today()
        self.path = path
        if self.path:
            self.trade_date_list: List[str] = self.get_trade_list()
            self.last_trade_date = self.get_last_trade_date()
            self.is_trade_date = self.today_is_trade_date(self.input_date)

    def get_trade_list(self) -> List[str]:
        trade_date_df = pd.read_csv(self.path)
        return trade_date_df["trade_date"].tolist()

    # 获取上一个交易日
    def get_last_trade_date(self) -> str:
        ind = self.trade_date_list.index("%s" % self.input_date)
        return self.trade_date_list[ind - 1]

    # 判断是不是交易日
    def today_is_trade_date(self, day: datetime.date):
        if str(day) in self.trade_date_list:
            return True
        return False

    # 判断是不是每年的1月1号
    def is_fst_date(self, day: datetime.date):
        if day.month == 1 and day.day == 1:
            return True
        return False

    def get_quick_info_timedelta(self) -> Tuple[float, float]:
        start_time = datetime.datetime(year=self.input_date.year, month=self.input_date.month, day=self.input_date.day,
                                       hour=9, minute=20, second=0)
        end_time = datetime.datetime(year=self.input_date.year, month=self.input_date.month, day=self.input_date.day,
                                     hour=9, minute=46, second=0)
        start_time_timestamp = time.mktime(start_time.timetuple())
        end_time_timestamp = time.mktime(end_time.timetuple())
        return start_time_timestamp, end_time_timestamp
