import requests
import re
import time
from userinput import get_uesr_inpt
# 引入字节编码
from urllib.parse import quote
# 引入beautifulsoup
from bs4 import BeautifulSoup
# 引入re
import re

HEADER = {'User-Agent': 'Mozilla/5.0'}
# 获取cookie
BASIC_URL = 'http://kns.cnki.net/kns/brief/result.aspx'
# 利用post请求先行注册一次
SEARCH_HANDLE_URL = 'http://kns.cnki.net/kns/request/SearchHandler.ashx'
# 发送get请求获得文献资源
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
        static_post_data = {
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
            'his': '0',
            'db_cjfqview': '中国学术期刊网络出版总库,WWJD',
            'db_cflqview': '中国学术期刊网络出版总库',
            '__': time.asctime(time.localtime()) + ' GMT+0800 (中国标准时间)'
        }
        # 将固定字段与自定义字段组合
        post_data={**static_post_data,**ueser_input}
        # 必须有第一次请求，否则会提示服务器没有用户
        first_post_res = self.session.post(
            SEARCH_HANDLE_URL, data=post_data, headers=HEADER)
        # get请求中需要传入第一个检索条件的值
        key_value=quote(ueser_input.get('txt_1_value1'))
        second_get_url = GET_PAGE_URL + first_post_res.text + '&t=1544249384932&keyValue='+key_value+'&S=1&sorttype='
        second_get_res= self.session.get(second_get_url,headers=HEADER)

        parse_page(pre_parse_page(second_get_res.text), second_get_res.text)


def pre_parse_page(page_source):
    '''
    用户选择需要检索的页数
    '''
    literature_num_pattern_compile=re.compile(r'.*?找到&nbsp;(.*?)&nbsp;')
    literature_num=re.search(literature_num_pattern_compile,page_source).group(1)
    literature_num_int=int(literature_num.replace(',',''))
    print('检索到' + literature_num + '条结果，全部下载大约需要' +
          s2h(literature_num_int)+'。')
    is_all_download=input('是否要全部下载（y/n）?')
    # 将所有数量根据每页20计算多少页
    if is_all_download=='y':
        page,i = divmod(literature_num_int,20)
        if i!=0:
            page+=1
        return page
    else:
        select_download_num=int(input('请输入需要下载的数量：'))
        while True:
            if select_download_num > literature_num_int:
                print('输入数量大于检索结果，请重新输入！')
                select_download_num=int(input('请输入需要下载的数量：'))
            else:
                page, i = divmod(select_download_num, 20)
                if i != 0:
                    page += 1
                return page

def parse_page(download_page_num,page_source):
    '''
    保存页面信息
    解析每一页的下载地址
    '''
    soup=BeautifulSoup(page_source,'lxml')
    tr_info = soup.findAll(name='table', attrs={'class': 'GridTableContent'})
    print(tr_info)


def s2h(seconds):
    '''
    将秒数转为小时数
    '''
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return("%02d小时%02d分钟%02d秒" % (h, m, s))


def main():
    search=SearchTools()
    search.search_literature(get_uesr_inpt())


if __name__=='__main__':
    main()