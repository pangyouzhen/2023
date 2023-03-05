import functools
from datetime import datetime
import pandas as pd
from loguru import logger

now = datetime.now().strftime("%Y-%m-%d")
logger.add(f"log/{now}.log")


@logger.catch
def func_utils(csv_path, csv_name, table_name, df):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            try:
                logger.info(f"{func.__name__}的参数{csv_path}{csv_name}{table_name}")
                result = func(*args, **kw)
                print(args)
                print(kw)
                result["date"] = now
                result.to_csv(
                    f"{csv_path}/{csv_name}_{now}.csv", index=False, encoding="utf-8"
                )
                logger.info(f"{func.__name__}_{now}存储csv数据成功")
                return result
            except Exception as e:
                logger.info(e)
                return pd.DataFrame()

        return wrapper

    return decorator
