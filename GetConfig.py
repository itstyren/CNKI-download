"""
-------------------------------------------------
   File Name：     GetConfig.py
   Description :   获取配置信息
   Author :        Cyrus_Ren
   date：          2018/12/10
-------------------------------------------------
   Change Activity:
                   
-------------------------------------------------
"""
__author__ = 'Cyrus_Ren'

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

    @LazyProperty
    def crawl_iscrackcode(self):
        return self.conf.get('crawl', 'isCrackCode')

    @LazyProperty
    def crawl_headers(self):
        headers = {
            'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
            'Host':
            'kns.cnki.net',
            'Connection':
            'keep-alive',
            'Cache-Control':
            'max-age=0',
        }
        return headers

    @LazyProperty
    def crawl_isdetail(self):
        return self.conf.get('crawl', 'isDetailPage')

    @LazyProperty
    def crawl_stepWaitTime(self):
        return int(self.conf.get('crawl', 'stepWaitTime'))

    @LazyProperty
    def crawl_isDownLoadLink(self):
        return int(self.conf.get('crawl', 'isDownLoadLink'))


config=GetConfig()
