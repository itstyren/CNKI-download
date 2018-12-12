import requests
import re
import time, os, shutil,logging
from UserInput import get_uesr_inpt
from GetConfig import config
from CrackVerifyCode import crack
# 引入字节编码
from urllib.parse import quote
# 引入beautifulsoup
from bs4 import BeautifulSoup

HEADER = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
    'Host': 'kns.cnki.net',
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
}
# 获取cookie
BASIC_URL = 'http://kns.cnki.net/kns/brief/result.aspx'
# 利用post请求先行注册一次
SEARCH_HANDLE_URL = 'http://kns.cnki.net/kns/request/SearchHandler.ashx'
# 发送get请求获得文献资源
GET_PAGE_URL = 'http://kns.cnki.net/kns/brief/brief.aspx?pagename='
# 下载的基础链接
DOWNLOAD_URL = 'http://kns.cnki.net/kns/'
# 切换页面基础链接
CHANGE_PAGE_URL = 'http://kns.cnki.net/kns/brief/brief.aspx'


class SearchTools(object):
    '''
    构建搜索类
    实现搜索方法
    '''

    def __init__(self):
        self.session = requests.Session()
        self.cur_page_num = 1
        # 保持会话
        self.session.get(BASIC_URL, headers=HEADER)

    def search_reference(self, ueser_input):
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
            'PageName': 'ASP.brief_default_result_aspx',
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
        post_data = {**static_post_data, **ueser_input}
        # 必须有第一次请求，否则会提示服务器没有用户
        first_post_res = self.session.post(
            SEARCH_HANDLE_URL, data=post_data, headers=HEADER)
        # get请求中需要传入第一个检索条件的值
        key_value = quote(ueser_input.get('txt_1_value1'))
        second_get_url = GET_PAGE_URL + first_post_res.text + '&t=1544249384932&keyValue=' + key_value + '&S=1&sorttype='
        # 检索结果的第一个页面
        second_get_res = self.session.get(second_get_url, headers=HEADER)
        change_page_pattern_compile = re.compile(
            r'.*?pagerTitleCell.*?<a href="(.*?)".*')
        self.change_page_url = re.search(change_page_pattern_compile,
                                         second_get_res.text).group(1)
        self.parse_page(
            self.pre_parse_page(second_get_res.text), second_get_res.text)

    def pre_parse_page(self, page_source):
        '''
        用户选择需要检索的页数
        '''
        reference_num_pattern_compile = re.compile(r'.*?找到&nbsp;(.*?)&nbsp;')
        reference_num = re.search(reference_num_pattern_compile,
                                  page_source).group(1)
        reference_num_int = int(reference_num.replace(',', ''))
        print('检索到' + reference_num + '条结果，全部下载大约需要' +
              s2h(reference_num_int * 5) + '。')
        is_all_download = input('是否要全部下载（y/n）?')
        # 将所有数量根据每页20计算多少页
        if is_all_download == 'y':
            page, i = divmod(reference_num_int, 20)
            if i != 0:
                page += 1
            return page
        else:
            select_download_num = int(input('请输入需要下载的数量：'))
            while True:
                if select_download_num > reference_num_int:
                    print('输入数量大于检索结果，请重新输入！')
                    select_download_num = int(input('请输入需要下载的数量（不满一页将下载整页）：'))
                else:
                    page, i = divmod(select_download_num, 20)
                    print("开始下载前%d页所有文件，预计用时%s" % (page, s2h(page * 20 * 5)))
                    print('－－－－－－－－－－－－－－－－－－－－－－－－－－')
                    if i != 0:
                        page += 1
                    return page

    def parse_page(self, download_page_left, page_source):
        '''
        保存页面信息
        解析每一页的下载地址
        '''
        soup = BeautifulSoup(page_source, 'lxml')
        # 定位到内容表区域
        tr_table = soup.find(name='table', attrs={'class': 'GridTableContent'})
        # 处理验证码
        try:
            # 去除第一个tr标签（表头）
            tr_table.tr.extract()
        except Exception as e:
            logging.error('出现验证码')
            return self.parse_page(download_page_left,
                crack.get_image(self.next_page_url, self.session, page_source,
                                HEADER))
        # 遍历每一行
        for index, tr_info in enumerate(tr_table.find_all(name='tr')):
            # 遍历每一列
            tr_text = ''
            download_url = ''
            for index, td_info in enumerate(tr_info.find_all(name='td')):
                # 因为一列中的信息非常杂乱，此处进行二次拼接
                td_text = ''
                for string in td_info.stripped_strings:
                    td_text += string
                tr_text += td_text + ' '
                with open('data/ReferenceList.txt', 'a', encoding='utf-8') as file:
                    file.write(td_text + ' ')
                # 寻找下载链接
                url = td_info.find('a', attrs={'class': 'briefDl_D'})
                if url:
                    download_url = url.attrs['href']
            # 将每一篇文献的信息分组
            single_refence_list = tr_text.split(' ')
            download_refence(download_url, single_refence_list)
            # 在每一行结束后输入一个空行
            with open('data/ReferenceList.txt', 'a', encoding='utf-8') as file:
                file.write('\n')
        # download_page_left为剩余等待遍历页面
        if download_page_left > 1:
            self.cur_page_num += 1
            self.get_another_page(download_page_left)

    def get_another_page(self, download_page_left):
        '''
        请求其他页面和请求第一个页面形式不同
        重新构造请求
        '''
        # time.sleep(5)
        curpage_pattern_compile = re.compile(r'.*?curpage=(\d+).*?')
        self.next_page_url = CHANGE_PAGE_URL + re.sub(
            curpage_pattern_compile, '?curpage=' + str(self.cur_page_num),
            self.change_page_url)
        get_res = self.session.get(self.next_page_url, headers=HEADER)
        download_page_left -= 1
        self.parse_page(download_page_left, get_res.text)


def download_refence(url, single_refence_list):
    '''
    拼接下载地址
    进行文献下载
    '''
    print('正在下载: ' + single_refence_list[1] + '.caj')
    name = single_refence_list[1] + '_' + single_refence_list[2]
    # 检查文件命名，防止网站资源有特殊字符本地无法保存
    file_pattern_compile = re.compile(r'[\\/:\*\?"<>\|]')
    name = re.sub(file_pattern_compile, '', name)
    # 拼接下载地址
    download_url = DOWNLOAD_URL + re.sub(r'../', '', url)
    # 保存下载链接
    with open('data/Links.txt', 'a', encoding='utf-8') as file:
        file.write(download_url+'\n')
    # 检查是否开启下载模式
    if config.crawl_isdownload==1:
        if not os.path.isdir('data/CAJs'):
            os.mkdir(r'data/CAJs')
        refence_file=requests.get(download_url,headers=HEADER)
        with open('CAJs\\' + name + '.caj', 'wb') as file:
            file.write(refence_file.content)
        time.sleep(5)


def s2h(seconds):
    '''
    将秒数转为小时数
    '''
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return ("%02d小时%02d分钟%02d秒" % (h, m, s))


def main():
    if os.path.isdir('data'):
        # 递归删除文件
        shutil.rmtree('data')
    # 创建一个空的
    os.mkdir('data')
    search = SearchTools()
    search.search_reference(get_uesr_inpt())


if __name__ == '__main__':
    main()