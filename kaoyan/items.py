# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class KaoyanItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    #学校名
    school_name = scrapy.Field()
    #标签名
    tag_name = scrapy.Field()
    #文章标题
    content_title = scrapy.Field()
    #内容
    content = scrapy.Field()
    #附件地址
    accessory_pdf = scrapy.Field()
    #附件名
    accessory_name =scrapy.Field()

    src = scrapy.Field()

    sid = scrapy.Field()

    download_status = scrapy.Field()
