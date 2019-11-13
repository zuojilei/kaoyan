# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import os,time,requests,pdfkit
from kaoyan.db.reports_mongo import ReportsDao
from kaoyan.tool.common_def import str_wash

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
        self.mongo = ReportsDao()
        self.mongo.set_collects('kaoyan')

    def process_item(self, item, spider):
        if self.mongo.is_exist_sid(item['sid']):
            self.mongo.insert_one(str_wash(dict(item)))
            dir_path = self.file_path(item)
            self.content_pdf(item, dir_path)
            # time.sleep(2)
            # self.download_pdf(item, dir_path)
        return item

    def file_path(self, item):
        if item['province'] and item['school_name'] and item['tag_name'] and item['content_title']:
            dir_path = 'D:\\data\\%s\\%s\\%s\\%s\\' % (item['province'],item['school_name'],item['tag_name'], item['content_title'])
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
                try:
                    response = requests.get(url=pdf, timeout=15, verify=False)
                    if response.status_code != 200:
                        print(response.url, response.status_code)
                        continue
                    else:
                        # 下载pdf
                        if 'pdf' in pdf:
                            accessory_path = dir_path + pdf_name + '.pdf'
                            with open(accessory_path, 'wb') as f:
                                f.write(response.content)
                                time.sleep(1)
                                print('*************pdf文件下载成功**************')

                        # 下载压缩包zip格式
                        elif pdf.endswith('.zip'):
                            accessory_path = dir_path + pdf_name + '.zip'
                            with open(accessory_path, 'wb') as f:
                                f.write(response.content)
                                time.sleep(1)
                                print('*************zip文件下载成功**************')

                        # 下载压缩包rar格式
                        elif pdf.endswith('.rar'):
                            accessory_path = dir_path + pdf_name + '.rar'
                            with open(accessory_path, 'wb') as f:
                                f.write(response.content)
                                time.sleep(1)
                                print('*************rar文件下载成功**************')

                        # 下载doc文档
                        elif 'doc' in pdf:
                            accessory_path = dir_path + pdf_name + '.doc'
                            with open(accessory_path, 'wb') as f:
                                f.write(response.content)
                                time.sleep(1)
                                print('*************doc文件下载成功**************')

                        # 下载docx文档
                        elif 'docx' in pdf:
                            accessory_path = dir_path + pdf_name + '.docx'
                            with open(accessory_path, 'wb') as f:
                                f.write(response.content)
                                time.sleep(1)
                                print('*************docx文件下载成功**************')

                        # 下载ppt
                        elif 'PPT' in pdf or 'ppt' in pdf:
                            accessory_path = dir_path + pdf_name + '.ppt'
                            with open(accessory_path, 'wb') as f:
                                f.write(response.content)
                                time.sleep(1)
                                print('*************ppt文件下载成功**************')

                        # 下载pptx
                        elif 'pptx' in pdf:
                            accessory_path = dir_path + pdf_name + '.pptx'
                            with open(accessory_path, 'wb') as f:
                                f.write(response.content)
                                time.sleep(1)
                                print('*************ppt文件下载成功**************')

                        # 下载表格xlsx格式
                        elif 'XLSx' in pdf or 'xlsx' in pdf:
                            accessory_path = dir_path + pdf_name + '.xlsx'
                            with open(accessory_path, 'wb') as f:
                                f.write(response.content)
                                time.sleep(1)
                                print('*************xlsx文件下载成功**************')

                        # 下载表格xls格式
                        elif 'XLS' in pdf or 'xls' in pdf:
                            accessory_path = dir_path + pdf_name + '.xls'
                            with open(accessory_path, 'wb') as f:
                                f.write(response.content)
                                time.sleep(1)
                                print('*************xls文件下载成功**************')
                        else:
                            return None
                except Exception as e:
                    print(e)
                    continue

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
            print('*************网页合成pdf成功*****************')
            return item
        except Exception as e:
            print(e)
