import platform
import json


def get_platform_path():
    if platform.system() == "Windows":
        parent_path = "D:"
    else:
        parent_path = "/data/"
    return parent_path


parent_path = get_platform_path()


def parser_js(x: str, keys_: str):
    js = json.loads(x)
    k = keys_.split(".")
    try:
        for i in k:
            if i == "$":
                # 1. 仅有一个key 2. key是不确定的
                k = "".join(list(js.keys()))
                js = js[k]
                continue
            js = js[i]
    except KeyError:
        return None
    except AttributeError:
        return None
    return js
