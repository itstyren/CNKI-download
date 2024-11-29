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
# from GetConfig import config
import re
import math, random
from GetConfig import config

HEADER = config.crawl_headers


class PageDetail(object):
    def __init__(self):
        # count用于计数excel行
        self.excel = xlwt.Workbook(encoding='utf8')
        self.sheet = self.excel.add_sheet('文献列表', True)
        self.set_style()
        self.sheet.write(0, 0, '序号', self.basic_style)
        self.sheet.write(0, 1, '题名', self.basic_style)
        self.sheet.write(0, 2, '作者', self.basic_style)
        self.sheet.write(0, 3, '单位', self.basic_style)
        self.sheet.write(0, 4, '关键字', self.basic_style)
        self.sheet.write(0, 5, '摘要', self.basic_style)
        self.sheet.write(0, 6, '来源', self.basic_style)
        self.sheet.write(0, 7, '发表时间', self.basic_style)
        self.sheet.write(0, 8, '数据库', self.basic_style)
        if config.crawl_isDownLoadLink == '1':
            self.sheet.write(0, 9, '下载地址', self.basic_style)

        # 生成userKey,服务器不做验证
        self.cnkiUserKey = self.set_new_guid()

    def get_detail_page(self, session, result_url, page_url,
                        single_refence_list, download_url):
        '''
        发送三次请求
        前两次服务器注册 最后一次正式跳转
        '''
        # 这个header必须设置
        HEADER['Referer'] = result_url
        self.single_refence_list = single_refence_list
        self.session = session
        self.session.cookies.set('cnkiUserKey', self.cnkiUserKey)
        self.download_url = download_url
        cur_url_pattern_compile = re.compile(
            r'.*?FileName=(.*?)&.*?DbCode=(.*?)&')
        cur_url_set = re.search(cur_url_pattern_compile, page_url)
        # 前两次请求需要的验证参数
        params = {
            'curUrl': 'detail.aspx?dbCode=' + cur_url_set.group(2) + '&fileName=' + cur_url_set.group(1),
            'referUrl': result_url + '#J_ORDER&',
            'cnkiUserKey': self.session.cookies['cnkiUserKey'],
            'action': 'file',
            'userName': '',
            'td': '1544605318654'
        }
        # 首先向服务器发送两次预请求
        self.session.get(
            'http://i.shufang.cnki.net/KRS/KRSWriteHandler.ashx',
            headers=HEADER,
            params=params)
        self.session.get(
            'http://kns.cnki.net/KRS/KRSWriteHandler.ashx',
            headers=HEADER,
            params=params)
        page_url = 'http://kns.cnki.net' + page_url
        get_res = self.session.get(page_url, headers=HEADER)
        self.pars_page(get_res.text)
        self.excel.save('data/Reference_detail.xls')

    def pars_page(self, detail_page):
        '''
        解析页面信息
        '''
        soup = BeautifulSoup(detail_page, 'lxml')
        # print(soup)

        # 获取作者单位信息
        self.orgn = ''
        # orgn_list = soup.find(name='div', class_='orgn').find_all('a')
        if soup.find(name='a', class_='author'):
            orgn_list = soup.find(name='a', class_='author').strings
        # print("====作者单位====")
        # print(orgn_list[1].string)

        # self.orgn = ''
            for o in orgn_list:
                    self.orgn += o
        else:
            self.orgn = '无单位来源'


        # 获取来源信息

        self.srcinfo = ''
        # srcinfo_list = soup.find(name='div', class_='sourinfo').find_all('p')
        if soup.find(name='div', class_='top-tip'):
            srcinfo_list = soup.find(name='div', class_='top-tip').find_all('a')

        # print("======来源信息=====")
        # print(srcinfo_list)

            if len(srcinfo_list) == 0:
                self.srcinf = '无来源信息'
            else:
                for s in srcinfo_list:
                    if s.string is not None:
                        self.srcinfo += s.string.strip() + '\n'
        else:
            self.srcinfo = '无来源信息'



        # 获取摘要

        self.abstract = ''
        if soup.find(name='span', id='ChDivSummary'):
            abstract_list = soup.find(name='span', id='ChDivSummary').strings
            for a in abstract_list:
                self.abstract += a
        else:
            self.abstract = '无摘要'

        # print("======摘要=====")
        # print(self.abstract)

        # else:
        #     abstract_list = '无摘要'
        # for a in abstract_list:
        #     self.abstract += a


        # 获取关键词

        self.keywords = ''
        # keywords_list = soup.find(name='label', id='catalog_KEYWORD').next_siblings
        if soup.find(name='p', class_='keywords'):
            keywords_list = soup.find(name='p', class_='keywords').find_all('a')
            if len(keywords_list) == 0:
                self.keywords = '无关键词'
            else:
                for k_l in keywords_list:
                    for k in k_l.stripped_strings:
                        self.keywords += k
        else:
            self.keywords = '无关键词'

        # print("======关键词=====")
        # print(keywords_list)

        # for k_l in keywords_list:
        #     # 去除关键词中的空格，换行
        #     for k in k_l.stripped_strings:
        #         self.keywords += k


        self.wtire_excel()

    def create_list(self):
        '''
        整理excel每一行的数据
        序号 题名 作者 单位 关键字 摘要  来源 发表时间 数据库
        '''
        self.reference_list = []
        for i in range(0, 3):
            self.reference_list.append(self.single_refence_list[i])  # 编号 书名 作者
        self.reference_list.append(self.orgn)  # 单位
        self.reference_list.append(self.keywords)  # 关键字
        self.reference_list.append(self.abstract)  # 摘要
        self.reference_list.append(self.srcinfo)  # 来源
        self.reference_list.append(self.single_refence_list[4])  # 日期
        self.reference_list.append(self.single_refence_list[5])  # 数据库
        if config.crawl_isDownLoadLink == '1':
            self.reference_list.append(self.download_url)

    def wtire_excel(self):
        '''
        将获得的数据写入到excel
        '''
        self.create_list()
        if config.crawl_isDownLoadLink == '1':
            for i in range(0, 10):
                self.sheet.write(int(self.reference_list[0]), i, self.reference_list[i], self.basic_style)
        else:
            for i in range(0, 9):
                self.sheet.write(int(self.reference_list[0]), i, self.reference_list[i], self.basic_style)

    def set_style(self):
        '''
        设置excel样式
        '''
        self.sheet.col(1).width = 256 * 30
        self.sheet.col(2).width = 256 * 15
        self.sheet.col(3).width = 256 * 20
        self.sheet.col(4).width = 256 * 20
        self.sheet.col(5).width = 256 * 60
        self.sheet.col(6).width = 256 * 15
        self.sheet.col(9).width = 256 * 15
        self.sheet.row(0).height_mismatch = True
        self.sheet.row(0).height = 20 * 20
        self.basic_style = xlwt.XFStyle()
        al = xlwt.Alignment()
        # 垂直对齐
        al.horz = al.HORZ_CENTER
        # 水平对齐
        al.vert = al.VERT_CENTER
        # 换行
        al.wrap = al.WRAP_AT_RIGHT
        # 设置边框
        borders = xlwt.Borders()
        borders.left = 6
        borders.right = 6
        borders.top = 6
        borders.bottom = 6

        self.basic_style.alignment = al
        self.basic_style.borders = borders

    def set_new_guid(self):
        '''
        生成用户秘钥
        '''
        guid = ''
        for i in range(1, 32):
            n = str(format(math.floor(random.random() * 16.0), 'x'))
            guid += n
            if (i == 8) or (i == 12) or (i == 16) or (i == 20):
                guid += "-"
        return guid


# 实例化
page_detail = PageDetail()
