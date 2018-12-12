"""
-------------------------------------------------
   File Name：     GetPageDetail.py
   Description :   获取文献摘要等信息存储至excel
   Author :        Cyrus_Ren
   date：          2018/12/12
-------------------------------------------------
   Change Activity:
                   
-------------------------------------------------
"""
__author__ = 'Cyrus_Ren'

import xlwt
from bs4 import BeautifulSoup
from GetConfig import config
import re
import math,random

HEADER = config.crawl_headers


class PageDetail(object):
    def __init__(self):
        excel = xlwt.Workbook(encoding='utf8')
        sheet = excel.add_sheet('文献列表', True)
        self.cnkiUserKey=self.set_new_guid()


    def get_detail_page(self, session,result_url, page_url, single_refence_list):
        '''
        发送三次请求
        前两次服务器注册 最后一次正式跳转
        '''
        self.session = session
        self.session.cookies.set('cnkiUserKey', self.cnkiUserKey)
        print(session.cookies)
        cur_url_pattern_compile = re.compile(
            r'.*?FileName=(.*?)&.*?DbCode=(.*?)&')
        cur_url_set=re.search(cur_url_pattern_compile,page_url)
        # 前两次请求需要的验证参数
        params = {
            'curUrl':'detail.aspx?dbCode=' + cur_url_set.group(2) + '&fileName='+cur_url_set.group(1),
            'referUrl': result_url+'#J_ORDER&',
            'cnkiUserKey': self.session.cookies['cnkiUserKey'],
            'action': 'file',
            'userName': '',
            'td': '1544605318654'
        }
        # print(params)
        # page_url = 'http://kns.cnki.net' + page_url
        page_res = self.session.get(
            'http://i.shufang.cnki.net/KRS/KRSWriteHandler.ashx',
            headers=HEADER,
            params=params)
        # print(page_res.text)

    def set_new_guid(self):
        '''
        生成用户秘钥
        '''
        guid=''
        for i in range(1,32):
            n = str(format(math.floor(random.random() * 16.0),'x'))
            guid+=n
            if (i == 8) or (i == 12) or (i == 16) or (i == 20):
                guid += "-"
        return guid
page_detail = PageDetail()