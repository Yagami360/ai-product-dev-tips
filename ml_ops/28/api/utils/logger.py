# coding=utf-8
import os
import time
from datetime import datetime
from logging import getLogger

def log_decorator(logger):
    """
    メソッド先頭で `@logging` デコレーターを付与することで使用可能になる logger
    """
    def _logging(func):
        def _wrapper(*args, **kwds):
            print("{} {} {} {} args={} kwds={}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "INFO", func.__qualname__, "START", args, kwds))
            logger.info("{} {} {} {} args={} kwds={}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "INFO", func.__qualname__, "START", args, kwds))

            # `@logging` デコレーターを付与したメソッドで return されたときに call される
            rtn = func(*args, **kwds)
            print("{} {} {} {} return {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "INFO", func.__qualname__, "END", rtn))
            logger.info("{} {} {} {} return {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "INFO", func.__qualname__, "END", rtn))
            return rtn

        return _wrapper

    return _logging
