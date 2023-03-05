from stock.cls.cailianshe import Cls
from stock.sentiment.sentiment_analyse import SentimentAnalyse
from stock.utils.datetime_utils import DateUtils
from stock.utils.logger_utils import logger

from datetime import datetime
import akshare as ak


class Sentiment:
    def __init__(self, config):
        dateutils_config, raw_data_path, cls_config, analyse_config = self.parser_config(config)
        self.dateutils = DateUtils(**dateutils_config)
        self.input_date = self.dateutils.input_date
        self.last_trade_date = self.dateutils.last_trade_date
        self.cls = Cls(self.dateutils.input_date, **cls_config)
        self.sentiment_analyse = SentimentAnalyse(input_date=self.input_date, last_trade_date=self.last_trade_date,
                                                  path=raw_data_path, **analyse_config)

    def parser_config(self, config):
        dateutils_config = config.get("dateutils", {})
        raw_data = config.get("get_raw_data")
        raw_data_path = raw_data["path"]
        cls_config = config.get("cls", {})
        analyse_config = config.get("analyse", {})
        return dateutils_config, raw_data_path, cls_config, analyse_config

    def run(self):
        if self.dateutils.is_trade_date:
            logger.info("today is trade_date")
            # 获取财联社涨停分析
            logger.info("抓取财联社涨停数据分析")
            self.cls.cls_run()
            # 获取市场情绪监控表
            logger.info("运行市场情绪分析")
            self.sentiment_analyse.run()
            logger.info("获取em涨停分析")
            self.get_zt_ak()
            logger.info('结束')
        else:
            logger.info("不是交易日，略过")

    def get_zt_ak(self):
        today = datetime.today()
        today = str(today.date()).replace("-", "")
        stock_em_zt_pool_df = ak.stock_em_zt_pool(today)
        stock_em_zt_pool_df.to_csv("stock_em_zt_pool_df_%s.csv" % today, encoding='utf-8')
