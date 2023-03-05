import datetime
import math

import pandas as pd

from stock.sentiment.get_raw_data import RawData
from stock.utils.utils_ import parent_path


class SentimentAnalyse:
    def __init__(self, input_date: datetime.date, last_trade_date, path, **kwargs):
        """

        :type limit_up_data_path: 上一个涨停的交易日路径
        :type sentiment_data_path: 市场情绪监控表的数据
        :type path: 今日交易日的数据

        """
        self.raw_data = RawData(input_date=input_date, path=path)
        self.path = path
        self.input_date_str = str(input_date)
        self.last_trade_date = last_trade_date
        self.sentiment_data_path = kwargs["sentiment_data_path"]
        self.limit_up_data_path = kwargs["limit_up_data_path"]

    @staticmethod
    def high_open_ratio(df: pd.DataFrame):
        if df["settlement"] == 0:
            return 0
        return (df["high"] - df['settlement']) / df["settlement"] * 100

    # 新浪财经今日的数据进行处理
    def today_data(self, path: str):
        df = pd.read_csv("%s/%s.csv" % (path, self.input_date_str), encoding="utf-8")
        df["high_open_ratio"] = df.apply(self.high_open_ratio, axis=1)
        df["code"] = df["code"].astype(str)
        # 688 科创板数据
        df688 = df[df["code"].str.startswith("688")]
        # 300 创业板数据
        df300 = df[df["code"].str.startswith("300")]
        # 其他 主板数据
        df_main = df[(~df["code"].str.startswith("300")) & (~df["code"].str.startswith("688"))]
        return df, df688, df300, df_main

    # 市场情绪监控数据处理
    def sentiment_data(self):
        # 读取创业板数据
        # 读取主板数据
        main_board = pd.read_csv("%s/stock.csv" % self.sentiment_data_path, index_col=0)
        # start_board = pd.read_csv(self.sentiment_data_path / "start%s.csv" % (self.dayint[0:4]), index_col=0)
        last_limit_up_df = pd.read_csv("%s/limit_up%s.csv" % (self.limit_up_data_path, self.last_trade_date),
                                       encoding="utf-8")
        return main_board, last_limit_up_df

    def get_sentiment(self, df_main: pd.DataFrame, main_stock: pd.DataFrame, last_limit_up_df):
        """
        :param df_main: 每日的交易数据
        :param main_stock: 历史的市场情绪监控表，
        """

        def get_limit_up_data(x):
            if math.isnan(x):
                x = 1
            else:
                x += 1
            return x

        # 上涨数据
        increase_main = df_main[(df_main["changepercent"] > 0)]
        # 下跌数据
        decrease_main = df_main[(df_main["changepercent"] < 0)]
        print(increase_main.shape[0], decrease_main.shape[0])
        # main_stock.loc["%s" % today_int, "红盘"] = increase_main.shape[0]
        # main_stock.loc["%s" % today_int, "绿盘"] = decrease_main.shape[0]
        # 涨停
        limit_up = df_main[(df_main["changepercent"] > 9.9) & (df_main["changepercent"] < 11)]
        # 默认的涨停天数是一天
        limit_up_df = pd.merge(limit_up, last_limit_up_df, left_on="name", right_on="name", how="left")
        limit_up_df = limit_up_df[["name", "连续涨停天数(天)"]]
        limit_up_df["连续涨停天数(天)"] = limit_up_df["连续涨停天数(天)"].apply(get_limit_up_data)
        limit_up_df["连续涨停天数(天)"] = limit_up_df["连续涨停天数(天)"].astype(int)
        limit_up_df.to_csv("%s/limit_up%s.csv" % (self.limit_up_data_path, self.input_date_str), index=False)
        # 跌停
        limit_down = (df_main[(df_main["changepercent"] < -9.9) & (df_main["changepercent"] > -11)])
        # main_stock.loc["%s" % today_int, "涨停"] = limit_up.shape[0]
        # main_stock.loc["%s" % today_int, "跌停"] = limit_down.shape[0]
        # 炸板
        once_limit_up = df_main[(df_main["high_open_ratio"] > 9.9) & (df_main["high_open_ratio"] < 11)]
        once_limit_up_name = once_limit_up["name"].tolist()
        limit_up_name = limit_up["name"].tolist()
        once = [i for i in once_limit_up_name if i not in limit_up_name]
        # main_stock.loc["%s" % today_int, "炸板"] = len(once)
        # 3连板数据以上数据 及 3连板数据
        limit_up_df_three_above = limit_up_df[limit_up_df["连续涨停天数(天)"] > 3]
        # 3连板数据
        limit_up_df_three = limit_up_df[limit_up_df["连续涨停天数(天)"] == 3]
        # 2连板数据
        limit_up_df_two = limit_up_df[limit_up_df["连续涨停天数(天)"] == 2]
        # main_stock.loc["%s" % today_int, "2连板个股数"] = limit_up_df_two.shape[0]
        # main_stock.loc["%s" % today_int, "2连板个股"] = ";".join(limit_up_df_two["name"].tolist())
        # 连板数据
        limit_up_df_one = limit_up_df[limit_up_df["连续涨停天数(天)"] == 1]
        limit_up_df_three_above["连续涨停天数(天)"] = limit_up_df_three_above["连续涨停天数(天)"].astype(str)
        limit_up_df_three_above["data"] = limit_up_df_three_above["name"].str.cat(limit_up_df_three_above["连续涨停天数(天)"])
        # main_stock.loc["%s" % today_int, "连板个股数"] = limit_up_df_one.shape[0]
        today_df = pd.DataFrame(
            data={
                "红盘": increase_main.shape[0],
                "绿盘": decrease_main.shape[0],
                "涨停": limit_up.shape[0],
                "跌停": limit_down.shape[0],
                "炸板": len(once),
                "3连板以上个股数": limit_up_df_three_above.shape[0],
                "3连板以上个股": ";".join(limit_up_df_three_above["data"].tolist()),
                "3连板": limit_up_df_three.shape[0],
                "3连板个股": ";".join(limit_up_df_three["name"].tolist()),
                "2连板": limit_up_df_two.shape[0],
                "2连板个股": ";".join(limit_up_df_two["name"].tolist()),
                "连板": limit_up_df_one.shape[0],
            },
            index=[self.input_date_str]
        )
        main_stock = main_stock.append(today_df)
        return main_stock

    def run(self):
        self.raw_data.get_raw_data()
        df, df688, df300, df_main = self.today_data(self.path)
        main_board, last_limit_up_df = self.sentiment_data()
        res = self.get_sentiment(df_main, main_board, last_limit_up_df)
        res.to_csv("%s/stock.csv" % self.sentiment_data_path, encoding="utf-8")


if __name__ == '__main__':
    input_date = datetime.date(year=2021, month=3, day=11)
    sentiment_analyse = SentimentAnalyse(input_date, last_trade_date="2021-03-10",
                                         path=parent_path + "/project/stock/raw_data",
                                         sentiment_data_path=parent_path + "/project/stock/sentiment",
                                         limit_up_data_path=parent_path + "/project/stock/raw_data")
    sentiment_analyse.run()
