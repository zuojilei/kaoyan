import hashlib
import re
import zipfile
import os
import requests
import time
import calendar

from kaoyan.db.reports_mongo import ReportsDao

"""
此模块公用一些函数
"""

def gen_sid(url):
    """
    根据url 获取唯一指纹
    :param url:
    :return:
    """
    md5 = hashlib.md5()
    md5.update(url.encode('utf-8'))
    return md5.hexdigest()


def str_wash(data):
    """
    传入用过字典，把里面值是字符串的清洗一下。返回字典
    :param data:
    :return:
    """
    for k, v in data.items():
        if isinstance(v, str):
            data[k] = v.strip()
    return data


def parse_data(data, type):
    """
    格式化数据
    :param self:
    :param data:
    :param type: 默认值
    :return:
    """
    if not data:
        data = type
    return data

def deal_title(title):
    """
    标题处理
    :param title:
    :return:
    """
    title = title.replace('/', chr(ord('/')+65248)).replace('\\', chr(ord('\\')+65248)).replace(':', '：').replace('&nbsp;', ' ')
    title = title.replace('*', '+').replace('|', '&').replace('?', '？').replace('"', '’').replace(">", "'大于'").replace("<", "'小于'").replace('\r\n', ' ')
    return title

def filezip(filename_path):
    """
    解压.zip文件
    :param path:
    :return:
    """
    if os.path.splitext(filename_path)[1] == '.zip':
        print(os.path.dirname(filename_path))
        file_zip =  zipfile.ZipFile(filename_path)
        file_zip.extractall(os.path.dirname(filename_path))
        file_zip.close()
        print('解压成功')
        os.remove(filename_path)
        print('压缩文件删除')

def deal_content(content):
    pattern1 = re.compile(r'<div class="qqShare".*?>.*?</div>',re.S)
    pattern2 = re.compile(r'<script type="text/javascript">.*?</script>',re.S)
    pattern3 = re.compile(r'<!-- qq分享.*?>',re.S)
    pattern4 = re.compile(r'<p><strong>相关链接：.*?</p>',re.S)
    pattern5 = re.compile(r'<table width="618"><tbody>.*?</tbody></table>', re.S)
    pattern6 = re.compile(r'<table.*?>.*?<tbody><tr><td width="550"><strong>友情提示：.*?</td></tr></tbody></table>', re.S)
    pattern7 = re.compile(r'<br><br>点击【<a.*?</p>', re.S)

    content = pattern1.sub('', content)
    content = pattern2.sub('', content)
    content = pattern3.sub('', content)
    content = pattern4.sub('', content)
    content = pattern5.sub('', content)
    content = pattern6.sub('', content)
    content = pattern7.sub('</p>', content)

    content = content.replace('\s', '')
    content = content.replace('\n', '')
    content = content.replace('\r', '')
    content = content.replace('\t', '')
    content = content.replace('\xa0', '')
    content = content.replace('\r\n', '')
    content = content.replace('&amp;', '')
    content = content.replace('\u3000', '')
    return content



