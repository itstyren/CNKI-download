"""
-------------------------------------------------
   File Name：     CrackVerifyCode.py
   Description :   处理验证码
   Author :        Cyrus_Ren
   date：          2018/12/8
-------------------------------------------------
   Change Activity:
                   
-------------------------------------------------
"""
__author__ = 'Cyrus_Ren'

from PIL import Image
# import tesserocr
import re
from GetConfig import config
from urllib.parse import quote_plus, urlencode
from GetConfig import config

HEADER = config.crawl_headers


class CrackCode(object):
    def get_image(self, current_url, session, page_source):
        '''
        获取验证码图片
        '''
        self.header = HEADER
        self.session = session
        # 获得验证码图片地址
        imgurl_pattern_compile = re.compile(r'.*?<img src="(.*?)".*?')
        img_url = re.search(imgurl_pattern_compile, page_source).group(1)
        self.current_url = re.search(r'(.*?)#', current_url).group(1)
        self.re_current_url = re.search(r'.net(.*)', self.current_url).group(1)
        # 下载图片
        img_url = 'http://kns.cnki.net' + img_url
        image_res = self.session.get(img_url, headers=self.header)
        with open('data/crack_code.jpeg', 'wb') as file:
            file.write(image_res.content)
        # 是否自动识别
        if config.crawl_iscrackcode == 1:
            return self.crack_code()
        else:
            return self.handle_code()

    def crack_code(self):
        '''
        自动识别验证码
        '''
        image = Image.open('data/crack_code.jpeg')
        # 转为灰度图像
        image = image.convert('L')
        # 设定二值化阈值
        threshold = 127
        table = []
        for i in range(256):
            if i < threshold:
                table.append(0)
            else:
                table.append(1)
        iamge = image.point(table, '1')
        # result = tesserocr.image_to_text(image)
        # print(result)

    def handle_code(self):
        '''
        手动识别验证码
        '''
        image = Image.open('crack_code.jpeg')
        image.show()
        code = input('出现验证码，请手动输入：')
        return self.send_code(code)

    def send_code(self, code):
        '''
        发送验证码
        '''
        # 对发送链接进行处理
        re_url = quote_plus(self.re_current_url)
        re_url = re.sub(r'%2F', '%2f', re_url)
        re_url = re.sub(r'%3F', '%3f', re_url)
        re_url = re.sub(r'%3D', '%3d', re_url)
        send_url = 'http://kns.cnki.net/kns/brief/vericode.aspx?rurl=' + re_url + '&vericode=' + code
        self.header['Referer'] = send_url
        self.header['Upgrade-Insecure-Requests'] = '1'
        return self.session.get(send_url, headers=self.header).text


crack = CrackCode()
