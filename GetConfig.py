import os
import configparser

class LazyProperty(object):
    """
    LazyProperty
    explain: http://www.spiderpy.cn/blog/5/
    """

    def __init__(self, func):
        self.func = func

    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:
            value = self.func(instance)
            setattr(instance, self.func.__name__, value)
            return value


class GetConfig(object):
    """
    to get config from config.ini
    """
    def __init__(self):
        self.conf=configparser.ConfigParser()
        self.conf.read('./Config.ini', encoding='UTF-8')

    @LazyProperty
    def crawl_isdownload(self):
        return self.conf.get('crawl','isDownloadFile')


config=GetConfig()
