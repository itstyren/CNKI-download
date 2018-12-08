import requests
import re
import time
from userinput import get_uesr_inpt

HEADER = {'User-Agent': 'Mozilla/5.0'}
BASIC_URL = 'http://kns.cnki.net/kns/brief/result.aspx'
SEARCH_HANDLE_URL = 'http://kns.cnki.net/kns/request/SearchHandler.ashx'
GET_PAGE_URL='http://kns.cnki.net/kns/brief/brief.aspx?pagename='


class SearchTools(object):
    '''
    构建搜索类
    实现搜索方法
    '''
    def __init__(self):
        self.session=requests.Session()
        # 保持会话
        self.session.get(BASIC_URL,headers=HEADER)

    def search_literature(self,ueser_input):
        '''
        第一次发送post请求
        再一次发送get请求,这次请求没有写文献等东西
        两次请求来获得文献列表
        '''
        post_data = {
            'action': '',
            'NaviCode': '*',
            'ua': '1.21',
            'isinEn': '1',
            'PageName': 'ASP.brief_result_aspx',
            'DbPrefix': 'SCDB',
            'DbCatalog': '中国学术期刊网络出版总库',
            'ConfigFile': 'CJFQ.xml',
            'db_opt': 'CJFQ,CDFD,CMFD,CPFD,IPFD,CCND,CCJD',  # 搜索类别（CNKI右侧的）
            'db_value': '中国学术期刊网络出版总库',
            'year_type': 'echar',
            'txt_1_sel': 'SU$%=|',  # 搜索类型默认为主题
            'txt_1_value1': 'sss',  # 搜索内容
            'txt_1_relation': '#CNKI_AND',
            "txt_1_special1": '=',
            'his': '0',
            'db_cjfqview': '中国学术期刊网络出版总库,WWJD',
            'db_cflqview': '中国学术期刊网络出版总库',
            '__': time.asctime(time.localtime()) + ' GMT+0800 (中国标准时间)'
        }
        # 必须有第一次请求，否则会提示服务器没有用户
        first_post_res = self.session.post(
            SEARCH_HANDLE_URL, data=post_data, headers=HEADER)

        second_get_url = GET_PAGE_URL + first_post_res.text + '&t=1544249384932&keyValue=sss&S=1&sorttype='
        second_get_res= self.session.get(second_get_url,headers=HEADER)
        # print(second_get_res.text)



def main():
    search=SearchTools()
    search.search_literature(get_uesr_inpt())


if __name__=='__main__':
    main()