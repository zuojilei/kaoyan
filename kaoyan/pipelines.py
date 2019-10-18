# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import os,time,requests,pdfkit

class KaoyanPipeline(object):

    def __init__(self):
        self.html_template =\
        """ 
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
        </head>
        <body>
        {}
        </body>
        </html>
        """

    def process_item(self, item, spider):
        dir_path = self.file_path(item)
        self.content_pdf(item, dir_path)
        time.sleep(2)
        self.download_pdf(item, dir_path)
        return item

    def file_path(self, item):
        if item['school_name'] and item['tag_name'] and item['content_title']:
            dir_path = 'C:\\data\\%s\\%s\\%s\\' % (item['school_name'],item['tag_name'], item['content_title'])
            is_exists = os.path.exists(dir_path)
            if not is_exists:
                os.makedirs(dir_path)
            return dir_path
        else:
            return None

    def file_write(self, item, dir_path):
        data = (self.html_template.format(item['content'])).encode('utf-8')
        file = dir_path + item['content_title'] + '.html'
        with open(file, 'wb') as f:
            f.write(data)

    def download_pdf(self, item, dir_path):
        if item['accessory_pdf'] and item['accessory_name']:
            for pdf, pdf_name in zip(item['accessory_pdf'], item['accessory_name']):
                # 下载pdf
                if 'pdf' in pdf:
                    data = requests.get(pdf).content
                    if data:
                        accessory_path = dir_path + pdf_name + '.pdf'
                        with open(accessory_path, 'wb') as f:
                            f.write(data)
                # 下载压缩包zip格式
                elif pdf.endswith('.zip'):
                    data = requests.get(pdf).content
                    if data:
                        accessory_path = dir_path + pdf_name + '.zip'
                        with open(accessory_path, 'wb') as f:
                            f.write(data)
                            time.sleep(1)
                # 下载压缩包rar格式
                elif pdf.endswith('.rar'):
                    data = requests.get(pdf).content
                    if data:
                        accessory_path = dir_path + pdf_name + '.rar'
                        with open(accessory_path, 'wb') as f:
                            f.write(data)
                            time.sleep(1)
                # 下载word文档
                elif 'doc' in pdf:
                    data = requests.get(pdf).content
                    if data:
                        accessory_path = dir_path + pdf_name + '.doc'
                        with open(accessory_path, 'wb') as f:
                            f.write(data)
                            time.sleep(1)
                # 下载ppt
                elif 'PPT' in pdf or 'ppt' in pdf:
                    data = requests.get(pdf).content
                    if data:
                        accessory_path = dir_path + pdf_name + '.ppt'
                        with open(accessory_path, 'wb') as f:
                            f.write(data)
                            time.sleep(1)
                # 下载表格xlsx格式
                elif 'XLSx' in pdf or 'xlsx' in pdf:
                    data = requests.get(pdf).content
                    if data:
                        accessory_path = dir_path + pdf_name + '.xlsx'
                        with open(accessory_path, 'wb') as f:
                            f.write(data)
                            time.sleep(1)
                        return True
                # 下载表格xls格式
                elif 'XLS' in pdf or 'xls' in pdf:
                    data = requests.get(pdf).content
                    if data:
                        accessory_path = dir_path + pdf_name + '.xls'
                        with open(accessory_path, 'wb') as f:
                            f.write(data)
                            time.sleep(1)
                        return True
                else:
                    return None

    def content_pdf(self, item, dir_path):
        """
        将content内容保存为pdf格式
        :param content:字符串
        :return:
        """
        html = (self.html_template.format(item['content']))
        path_wk = r'C:\soft\wkhtmltopdf\bin\wkhtmltopdf.exe'  # 安装位置
        try:
            file = dir_path + item['content_title'] + '.pdf'
            config = pdfkit.configuration(wkhtmltopdf=path_wk)
            pdfkit.from_string(html, file, configuration=config)
            item['download_status'] = 1
            # return item
        except Exception as e:
            print(e)
