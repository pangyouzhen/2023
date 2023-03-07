import argparse
import datetime
import sys
import time
from argparse import Namespace
from pathlib import Path

import akshare as ak
import openpyxl
import pandas as pd
from loguru import logger

from stock.cls.stock_cls_alerts import stock_zh_a_alerts_cls
from stock.cls.stock_cls_zt_analyse import stock_zh_a_zt_analyse_cls
from stock.utils.wraps_utils import func_utils

print('start------')
path = Path("./log")
logger.info(f"{path.absolute()}")
global trade_df
trade_df = pd.read_csv("./stock/tool_trade_date_hist_sina_df.csv")


# 今天的原始数据
@func_utils(
    csv_path="./raw_data/", csv_name="raw_data", table_name="everyday_data", df=trade_df
)
def get_raw_date(date,*args,**kwargs):
    stock_zh_a_spot_df = ak.stock_zh_a_spot()
    print(stock_zh_a_spot_df[:5])
    return stock_zh_a_spot_df


# 今天的cls zt分析数据
@logger.catch
def zt_analyse_df(date,*args,**kwargs):
    date = date.replace("-","")
    return stock_zh_a_zt_analyse_cls(date)


# zt 数据
@func_utils(csv_path="./raw_data/", csv_name="zt", table_name="zt", df=trade_df)
def get_zt_data(date,*args,**kwargs):
    date = date.replace("-", "")
    stock_em_zt_pool_df = ak.stock_em_zt_pool(date)
    return stock_em_zt_pool_df


# zb数据
@func_utils(csv_path="./raw_data/", csv_name="zb", table_name="zb", df=trade_df)
def get_zb_data(date,*args,**kwargs):
    date = date.replace("-", "")
    stock_em_zt_pool_zbgc_df = ak.stock_em_zt_pool_zbgc(date)
    return stock_em_zt_pool_zbgc_df


# dt数据
@func_utils(csv_path="./raw_data", csv_name="dt", table_name="dt", df=trade_df)
def get_dt_data(date,*args,**kwargs):
    date = date.replace("-", "")
    stock_em_zt_pool_dtgc_df = ak.stock_em_zt_pool_dtgc(date)
    return stock_em_zt_pool_dtgc_df


@logger.catch
def merge_data(date,*args,**kwargs):
    df = pd.read_excel("sentiment/stock2023.xlsx")
    raw_data = pd.read_csv(f"raw_data/raw_data_{date}.csv")
    zt_data = pd.read_csv(f"raw_data/zt_{date}.csv")
    dt_data_path = Path(f"raw_data/dt_{date}.csv")
    if dt_data_path.exists():
        dt_data = pd.read_csv(f"raw_data/dt_{date}.csv")
    else:
        dt_data = pd.DataFrame()
    zb_data = pd.read_csv(f"raw_data/zb_{date}.csv")
    increase = raw_data[raw_data["涨跌幅"] > 0]
    decrease = raw_data[raw_data["涨跌幅"] < 0]
    zt_num = zt_data.shape[0]
    
    above_three = zt_data[zt_data["连板数"] > 3].sort_values("连板数",ascending=False)
    above_three["连板数"] = above_three["连板数"].astype(str)
    above_three["val"] = above_three["名称"] + above_three["连板数"]

    three = zt_data[zt_data["连板数"] == 3]
    two = zt_data[zt_data["连板数"] == 2]
    one = zt_data[zt_data["连板数"] == 1]
    today_df = pd.DataFrame(
        [{
            "日期":date,
            "红盘": increase.shape[0],
            "绿盘": decrease.shape[0],
            "涨停": zt_num,
            "跌停": dt_data.shape[0],
            "炸板": zb_data.shape[0],
            "3连板以上个股数": above_three.shape[0],
            "3连板以上个股": ";".join(above_three["val"].tolist()),
            "3连板": three.shape[0],
            "3连板个股": ";".join(three["名称"].tolist()),
            "2连板": two.shape[0],
            "2连板个股": ";".join(two["名称"].tolist()),
            "首板": one.shape[0],
        }]
    )
    df = df.append(today_df)
    df.to_csv("sentiment/stock2023.csv",index=False)


def main(date,*args,**kwargs):
    if date in trade_df["trade_date"].tolist():
        # alerts_cls()
        get_raw_date(date)
        time.sleep(5)

        get_zt_data(date)
        time.sleep(20)

        get_dt_data(date)
        time.sleep(20)

        get_zb_data(date)
        time.sleep(20)

        zt_analyse_df(date)

        merge_data(date)
    else:
        logger.info("今天不是交易日")


FUNCTION_MAP = {
    "zt": get_zt_data,
    "dt": get_dt_data,
    "zt_analyse": zt_analyse_df,
    "zb": get_zb_data,
    "raw": get_raw_date,
    "all": main,
    "sentiment": merge_data,
    # "cls": alerts_cls,
}


def parse_para() -> Namespace:
    parser = argparse.ArgumentParser(description="获取市场情绪")
    parser.add_argument("--func", choices=FUNCTION_MAP.keys(), help="获取涨停数据")
    parser.add_argument("--date", default=str(datetime.datetime.today().date()))
    args = parser.parse_args()
    print(args)
    func = FUNCTION_MAP[args.func]
    func(date = args.date)

if __name__ == "__main__":
    sys.exit(parse_para())