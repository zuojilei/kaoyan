# -*- coding: utf-8 -*-
import scrapy,re, time
from kaoyan.items import KaoyanItem
from kaoyan.tool.common_def import *

class KaoyanOneSpider(scrapy.Spider):
    name = 'kaoyan_one'
    allowed_domains = ['kaoyan.com']
    start_urls = ['http://www.kaoyan.com/beijing/']
    base_url = 'http://www.kaoyan.com'
    custom_settings = {
        'ITEM_PIPELINES': {
            'kaoyan.pipelines.KaoyanPipeline': 300,
            # 'spider.pipeline.pipelines.ImageToPdfPipeline': 120,
            # 'spider.pipeline.pipelines.ReportsMssqlPipeline': 130,
        },
        'DOWNLOAD_DELAY': 1
    }

    def parse(self, response):
        elems = response.xpath('//dl[@class="schoolListItem"]')
        for elem in elems:
            school_name = elem.xpath('./dt/a/text()').extract_first()
            url = elem.xpath('./dd[@class="quickItem"]/a/@href').extract_first()
            meta = {'school_name':school_name if school_name else ''}
            if url:
                if 'http' not in url:
                    url = self.base_url + url
                yield scrapy.Request(url=url, callback=self.parse_tag_list, meta=meta,dont_filter=True)
            # break

    def parse_tag_list(self, response):
        elems = response.xpath('//ul[@class="subGuideList"]/li')
        del elems[7]
        for elem in elems:
            try:
                meta = response.meta
                tag_name = elem.xpath('./a/text()').extract_first()
                meta['tag_name'] = tag_name
                tag_url = elem.xpath('./a/@href').extract_first()
                if tag_url:
                    if 'http' not in tag_url:
                        tag_url = self.base_url + tag_url
                    yield scrapy.Request(url=tag_url, callback=self.parse_list, meta=meta, dont_filter=True)
            except Exception as e:
                print('获取标签地址错误', e)
                continue

    def parse_list(self, response):
        elems = response.xpath('//ul[@class="subList"]/li')
        for elem in elems:
            try:
                item = KaoyanItem()
                item['school_name'] = response.meta['school_name']
                item['tag_name'] = response.meta['tag_name']
                content_title = elem.xpath('./a/text()').extract_first()
                item['content_title'] = deal_title(content_title) if content_title else ''
                item['content'] = ''
                detail_url = elem.xpath('./a/@href').extract_first()
                if detail_url:
                    if 'http' not in detail_url:
                        detail_url = self.base_url + detail_url
                    yield scrapy.Request(url=detail_url, callback=self.parse_detail, meta={"item":item},dont_filter=True)
            except Exception as e:
                print('详情页地址不允许访问',e)
                continue
        # meta = response.meta
        # next_page_url = response.xpath('//div[@class="tPage"]/a[text()="下一页"]/@href').extract_first()
        # if next_page_url:
        #     if 'http' not in next_page_url:
        #         next_page_url = self.base_url + next_page_url
        #     yield scrapy.Request(url=next_page_url, callback=self.parse_list, meta=meta, dont_filter=True)

    def parse_detail(self, response):
        try:
            if response.status != 200:
                print(response.url, '：无响应', response.status)
                return
            else:
                item =response.meta['item']
                pdate = response.xpath('//div[@class="articleInfo"]/span[1]/text()').extract_first()
                if pdate:
                    pdate = pdate.split(' ')[0]
                    year = int(pdate.split('-')[0])
                    if year < 2017:
                        print('2017年以后的')
                        return
                    else:
                        item['src'] = response.url
                        item['sid'] =  gen_sid(response.url)
                        item['pdate'] = pdate
                        item['download_status'] = 0
                        accessory_pdfs = response.xpath('//div[@class="articleCon"]//a/@href').extract()
                        accessory_name = response.xpath('//div[@class="articleCon"]//a/text()').extract()
                        if accessory_pdfs:
                            accessory_pdf = []
                            for pdf in accessory_pdfs:
                                if 'http' not in pdf:
                                    pdf = self.base_url +pdf
                                accessory_pdf.append(pdf)
                            item['accessory_pdf'] = accessory_pdf
                            item['accessory_name'] = accessory_name
                        else:
                            item['accessory_pdf'] = []
                            item['accessory_name'] = []
                        content = response.xpath('//div[@class="article"]').extract_first()
                        if content:
                            content = content+'<br>'+ item['content']
                            next_url = response.xpath('//div[@class="tPage"]/a[text()="下一页"]/@href').extract_first()
                            if next_url:
                                item['content'] = deal_content(content) if content else ''
                                return scrapy.Request(url=next_url, callback=self.parse_detail, meta={'item':item}, dont_filter=True)
                            else:
                                item['content'] = deal_content(content) if content else ''
                        else:
                            item['content'] = ''
                        yield item
        except Exception as e:
            print(e, response.url)


class KaoyanTwoSpider(scrapy.Spider):
    name = 'kaoyan_two'
    allowed_domains = ['kaoyan.com']
    start_urls = ['http://www.kaoyan.com/beijing/']
    base_url = 'http://www.kaoyan.com'
    custom_settings = {
        'ITEM_PIPELINES': {
            'kaoyan.pipelines.KaoyanPipeline': 300,
            # 'spider.pipeline.pipelines.ImageToPdfPipeline': 120,
            # 'spider.pipeline.pipelines.ReportsMssqlPipeline': 130,
        },
        'DOWNLOAD_DELAY': 1
    }

    def parse(self, response):
        elems = response.xpath('//dl[@class="schoolListItem"]')[211:216]
        for elem in elems:
            school_name = elem.xpath('./dt/a/text()').extract_first()
            url = elem.xpath('./dd[@class="quickItem"]/a/@href').extract_first()
            meta = {'school_name': school_name if school_name else ''}
            if url:
                if 'http' not in url:
                    url = self.base_url + url
                yield scrapy.Request(url=url, callback=self.parse_tag_list, meta=meta, dont_filter=True)
            # break

    def parse_tag_list(self, response):
        elems = response.xpath('//ul[@class="subGuideList"]/li')
        del elems[7]
        for elem in elems:
            try:
                meta = response.meta
                tag_name = elem.xpath('./a/text()').extract_first()
                meta['tag_name'] = tag_name
                tag_url = elem.xpath('./a/@href').extract_first()
                if tag_url:
                    if 'http' not in tag_url:
                        tag_url = self.base_url + tag_url
                    yield scrapy.Request(url=tag_url, callback=self.parse_list, meta=meta, dont_filter=True)
            except Exception as e:
                print('获取标签地址错误', e)
                continue

    def parse_list(self, response):
        elems = response.xpath('//ul[@class="subList"]/li')
        for elem in elems:
            try:
                item = KaoyanItem()
                item['school_name'] = response.meta['school_name']
                item['tag_name'] = response.meta['tag_name']
                content_title = elem.xpath('./a/text()').extract_first()
                item['content_title'] = deal_title(content_title) if content_title else ''
                item['content'] = ''
                detail_url = elem.xpath('./a/@href').extract_first()
                if detail_url:
                    if 'http' not in detail_url:
                        detail_url = self.base_url + detail_url
                    yield scrapy.Request(url=detail_url, callback=self.parse_detail, meta={"item": item},
                                         dont_filter=True)
            except Exception as e:
                print('详情页地址不允许访问', e)
                continue
        meta = response.meta
        next_page_url = response.xpath('//div[@class="tPage"]/a[text()="下一页"]/@href').extract_first()
        if next_page_url:
            if 'http' not in next_page_url:
                next_page_url = self.base_url + next_page_url
            yield scrapy.Request(url=next_page_url, callback=self.parse_list, meta=meta, dont_filter=True)

    def parse_detail(self, response):
        try:
            if response.status != 200:
                print(response.url, '：无响应', response.status)
                return
            else:
                item = response.meta['item']
                pdate = response.xpath('//div[@class="articleInfo"]/span[1]/text()').extract_first()
                if pdate:
                    pdate = pdate.split(' ')[0]
                    year = int(pdate.split('-')[0])
                    if year < 2017:
                        print('2017年以后的')
                        return
                    else:
                        item['src'] = response.url
                        item['sid'] = gen_sid(response.url)
                        item['pdate'] = pdate
                        item['download_status'] = 0
                        accessory_pdfs = response.xpath('//div[@class="articleCon"]//a/@href').extract()
                        accessory_name = response.xpath('//div[@class="articleCon"]//a/text()').extract()
                        if accessory_pdfs:
                            accessory_pdf = []
                            for pdf in accessory_pdfs:
                                if 'http' not in pdf:
                                    pdf = self.base_url + pdf
                                accessory_pdf.append(pdf)
                            item['accessory_pdf'] = accessory_pdf
                            item['accessory_name'] = accessory_name
                        else:
                            item['accessory_pdf'] = []
                            item['accessory_name'] = []
                        content = response.xpath('//div[@class="article"]').extract_first()
                        if content:
                            content = content + '<br>' + item['content']
                            next_url = response.xpath('//div[@class="tPage"]/a[text()="下一页"]/@href').extract_first()
                            if next_url:
                                item['content'] = deal_content(content) if content else ''
                                return scrapy.Request(url=next_url, callback=self.parse_detail, meta={'item': item},
                                                      dont_filter=True)
                            else:
                                item['content'] = deal_content(content) if content else ''
                        else:
                            item['content'] = ''
                        yield item
        except Exception as e:
            print(e, response.url)


class KaoyanthreeSpider(scrapy.Spider):
    name = 'kaoyan_three'
    allowed_domains = ['kaoyan.com']
    start_urls = ['http://www.kaoyan.com/beijing/']
    base_url = 'http://www.kaoyan.com'
    custom_settings = {
        'ITEM_PIPELINES': {
            'kaoyan.pipelines.KaoyanPipeline': 300,
            # 'spider.pipeline.pipelines.ImageToPdfPipeline': 120,
            # 'spider.pipeline.pipelines.ReportsMssqlPipeline': 130,
        },
        'DOWNLOAD_DELAY': 1
    }

    def parse(self, response):
        elems = response.xpath('//dl[@class="schoolListItem"]')[121:131]
        for elem in elems:
            school_name = elem.xpath('./dt/a/text()').extract_first()
            url = elem.xpath('./dd[@class="quickItem"]/a/@href').extract_first()
            meta = {'school_name': school_name if school_name else ''}
            if url:
                if 'http' not in url:
                    url = self.base_url + url
                yield scrapy.Request(url=url, callback=self.parse_tag_list, meta=meta, dont_filter=True)
            # break

    def parse_tag_list(self, response):
        elems = response.xpath('//ul[@class="subGuideList"]/li')
        del elems[7]
        for elem in elems:
            try:
                meta = response.meta
                tag_name = elem.xpath('./a/text()').extract_first()
                meta['tag_name'] = tag_name
                tag_url = elem.xpath('./a/@href').extract_first()
                if tag_url:
                    if 'http' not in tag_url:
                        tag_url = self.base_url + tag_url
                    yield scrapy.Request(url=tag_url, callback=self.parse_list, meta=meta, dont_filter=True)
            except Exception as e:
                print('获取标签地址错误', e)
                continue

    def parse_list(self, response):
        elems = response.xpath('//ul[@class="subList"]/li')
        for elem in elems:
            try:
                item = KaoyanItem()
                item['school_name'] = response.meta['school_name']
                item['tag_name'] = response.meta['tag_name']
                content_title = elem.xpath('./a/text()').extract_first()
                item['content_title'] = deal_title(content_title) if content_title else ''
                item['content'] = ''
                detail_url = elem.xpath('./a/@href').extract_first()
                if detail_url:
                    if 'http' not in detail_url:
                        detail_url = self.base_url + detail_url
                    yield scrapy.Request(url=detail_url, callback=self.parse_detail, meta={"item": item},
                                         dont_filter=True)
            except Exception as e:
                print('详情页地址不允许访问', e)
                continue
        meta = response.meta
        next_page_url = response.xpath('//div[@class="tPage"]/a[text()="下一页"]/@href').extract_first()
        if next_page_url:
            if 'http' not in next_page_url:
                next_page_url = self.base_url + next_page_url
            yield scrapy.Request(url=next_page_url, callback=self.parse_list, meta=meta, dont_filter=True)

    def parse_detail(self, response):
        try:
            if response.status != 200:
                print(response.url, '：无响应', response.status)
                return
            else:
                item = response.meta['item']
                pdate = response.xpath('//div[@class="articleInfo"]/span[1]/text()').extract_first()
                if pdate:
                    pdate = pdate.split(' ')[0]
                    year = int(pdate.split('-')[0])
                    if year < 2017:
                        print('2017年以后的')
                        return
                    else:
                        item['src'] = response.url
                        item['sid'] = gen_sid(response.url)
                        item['pdate'] = pdate
                        item['download_status'] = 0
                        accessory_pdfs = response.xpath('//div[@class="articleCon"]//a/@href').extract()
                        accessory_name = response.xpath('//div[@class="articleCon"]//a/text()').extract()
                        if accessory_pdfs:
                            accessory_pdf = []
                            for pdf in accessory_pdfs:
                                if 'http' not in pdf:
                                    pdf = self.base_url + pdf
                                accessory_pdf.append(pdf)
                            item['accessory_pdf'] = accessory_pdf
                            item['accessory_name'] = accessory_name
                        else:
                            item['accessory_pdf'] = []
                            item['accessory_name'] = []
                        content = response.xpath('//div[@class="article"]').extract_first()
                        if content:
                            content = content + '<br>' + item['content']
                            next_url = response.xpath('//div[@class="tPage"]/a[text()="下一页"]/@href').extract_first()
                            if next_url:
                                item['content'] = deal_content(content) if content else ''
                                return scrapy.Request(url=next_url, callback=self.parse_detail, meta={'item': item},
                                                      dont_filter=True)
                            else:
                                item['content'] = deal_content(content) if content else ''
                        else:
                            item['content'] = ''
                        yield item
        except Exception as e:
            print(e, response.url)


class KaoyanFourSpider(scrapy.Spider):
    name = 'kaoyan_four'
    allowed_domains = ['kaoyan.com']
    start_urls = ['http://www.kaoyan.com/beijing/']
    base_url = 'http://www.kaoyan.com'
    custom_settings = {
        'ITEM_PIPELINES': {
            'kaoyan.pipelines.KaoyanPipeline': 300,
            # 'spider.pipeline.pipelines.ImageToPdfPipeline': 120,
            # 'spider.pipeline.pipelines.ReportsMssqlPipeline': 130,
        },
        'DOWNLOAD_DELAY': 1
    }

    def parse(self, response):
        elems = response.xpath('//dl[@class="schoolListItem"]')[131:141]
        for elem in elems:
            school_name = elem.xpath('./dt/a/text()').extract_first()
            url = elem.xpath('./dd[@class="quickItem"]/a/@href').extract_first()
            meta = {'school_name': school_name if school_name else ''}
            if url:
                if 'http' not in url:
                    url = self.base_url + url
                yield scrapy.Request(url=url, callback=self.parse_tag_list, meta=meta, dont_filter=True)
            # break

    def parse_tag_list(self, response):
        elems = response.xpath('//ul[@class="subGuideList"]/li')
        del elems[7]
        for elem in elems:
            try:
                meta = response.meta
                tag_name = elem.xpath('./a/text()').extract_first()
                meta['tag_name'] = tag_name
                tag_url = elem.xpath('./a/@href').extract_first()
                if tag_url:
                    if 'http' not in tag_url:
                        tag_url = self.base_url + tag_url
                    yield scrapy.Request(url=tag_url, callback=self.parse_list, meta=meta, dont_filter=True)
            except Exception as e:
                print('获取标签地址错误', e)
                continue

    def parse_list(self, response):
        elems = response.xpath('//ul[@class="subList"]/li')
        for elem in elems:
            try:
                item = KaoyanItem()
                item['school_name'] = response.meta['school_name']
                item['tag_name'] = response.meta['tag_name']
                content_title = elem.xpath('./a/text()').extract_first()
                item['content_title'] = deal_title(content_title) if content_title else ''
                item['content'] = ''
                detail_url = elem.xpath('./a/@href').extract_first()
                if detail_url:
                    if 'http' not in detail_url:
                        detail_url = self.base_url + detail_url
                    yield scrapy.Request(url=detail_url, callback=self.parse_detail, meta={"item": item},
                                         dont_filter=True)
            except Exception as e:
                print('详情页地址不允许访问', e)
                continue
        meta = response.meta
        next_page_url = response.xpath('//div[@class="tPage"]/a[text()="下一页"]/@href').extract_first()
        if next_page_url:
            if 'http' not in next_page_url:
                next_page_url = self.base_url + next_page_url
            yield scrapy.Request(url=next_page_url, callback=self.parse_list, meta=meta, dont_filter=True)

    def parse_detail(self, response):
        try:
            if response.status != 200:
                print(response.url, '：无响应', response.status)
                return
            else:
                item = response.meta['item']
                pdate = response.xpath('//div[@class="articleInfo"]/span[1]/text()').extract_first()
                if pdate:
                    pdate = pdate.split(' ')[0]
                    year = int(pdate.split('-')[0])
                    if year < 2017:
                        print('2017年以后的')
                        return
                    else:
                        item['src'] = response.url
                        item['sid'] = gen_sid(response.url)
                        item['pdate'] = pdate
                        item['download_status'] = 0
                        accessory_pdfs = response.xpath('//div[@class="articleCon"]//a/@href').extract()
                        accessory_name = response.xpath('//div[@class="articleCon"]//a/text()').extract()
                        if accessory_pdfs:
                            accessory_pdf = []
                            for pdf in accessory_pdfs:
                                if 'http' not in pdf:
                                    pdf = self.base_url + pdf
                                accessory_pdf.append(pdf)
                            item['accessory_pdf'] = accessory_pdf
                            item['accessory_name'] = accessory_name
                        else:
                            item['accessory_pdf'] = []
                            item['accessory_name'] = []
                        content = response.xpath('//div[@class="article"]').extract_first()
                        if content:
                            content = content + '<br>' + item['content']
                            next_url = response.xpath('//div[@class="tPage"]/a[text()="下一页"]/@href').extract_first()
                            if next_url:
                                item['content'] = deal_content(content) if content else ''
                                return scrapy.Request(url=next_url, callback=self.parse_detail, meta={'item': item},
                                                      dont_filter=True)
                            else:
                                item['content'] = deal_content(content) if content else ''
                        else:
                            item['content'] = ''
                        yield item
        except Exception as e:
            print(e, response.url)


class KaoyanFiveSpider(scrapy.Spider):
    name = 'kaoyan_five'
    allowed_domains = ['kaoyan.com']
    start_urls = ['http://www.kaoyan.com/beijing/']
    base_url = 'http://www.kaoyan.com'
    custom_settings = {
        'ITEM_PIPELINES': {
            'kaoyan.pipelines.KaoyanPipeline': 300,
            # 'spider.pipeline.pipelines.ImageToPdfPipeline': 120,
            # 'spider.pipeline.pipelines.ReportsMssqlPipeline': 130,
        },
        'DOWNLOAD_DELAY': 1
    }

    def parse(self, response):
        elems = response.xpath('//dl[@class="schoolListItem"]')[141:151]
        for elem in elems:
            school_name = elem.xpath('./dt/a/text()').extract_first()
            url = elem.xpath('./dd[@class="quickItem"]/a/@href').extract_first()
            meta = {'school_name': school_name if school_name else ''}
            if url:
                if 'http' not in url:
                    url = self.base_url + url
                yield scrapy.Request(url=url, callback=self.parse_tag_list, meta=meta, dont_filter=True)
            # break

    def parse_tag_list(self, response):
        elems = response.xpath('//ul[@class="subGuideList"]/li')
        del elems[7]
        for elem in elems:
            try:
                meta = response.meta
                tag_name = elem.xpath('./a/text()').extract_first()
                meta['tag_name'] = tag_name
                tag_url = elem.xpath('./a/@href').extract_first()
                if tag_url:
                    if 'http' not in tag_url:
                        tag_url = self.base_url + tag_url
                    yield scrapy.Request(url=tag_url, callback=self.parse_list, meta=meta, dont_filter=True)
            except Exception as e:
                print('获取标签地址错误', e)
                continue

    def parse_list(self, response):
        elems = response.xpath('//ul[@class="subList"]/li')
        for elem in elems:
            try:
                item = KaoyanItem()
                item['school_name'] = response.meta['school_name']
                item['tag_name'] = response.meta['tag_name']
                content_title = elem.xpath('./a/text()').extract_first()
                item['content_title'] = deal_title(content_title) if content_title else ''
                item['content'] = ''
                detail_url = elem.xpath('./a/@href').extract_first()
                if detail_url:
                    if 'http' not in detail_url:
                        detail_url = self.base_url + detail_url
                    yield scrapy.Request(url=detail_url, callback=self.parse_detail, meta={"item": item},
                                         dont_filter=True)
            except Exception as e:
                print('详情页地址不允许访问', e)
                continue
        meta = response.meta
        next_page_url = response.xpath('//div[@class="tPage"]/a[text()="下一页"]/@href').extract_first()
        if next_page_url:
            if 'http' not in next_page_url:
                next_page_url = self.base_url + next_page_url
            yield scrapy.Request(url=next_page_url, callback=self.parse_list, meta=meta, dont_filter=True)

    def parse_detail(self, response):
        try:
            if response.status != 200:
                print(response.url, '：无响应', response.status)
                return
            else:
                item = response.meta['item']
                pdate = response.xpath('//div[@class="articleInfo"]/span[1]/text()').extract_first()
                if pdate:
                    pdate = pdate.split(' ')[0]
                    year = int(pdate.split('-')[0])
                    if year < 2017:
                        print('2017年以后的')
                        return
                    else:
                        item['src'] = response.url
                        item['sid'] = gen_sid(response.url)
                        item['pdate'] = pdate
                        item['download_status'] = 0
                        accessory_pdfs = response.xpath('//div[@class="articleCon"]//a/@href').extract()
                        accessory_name = response.xpath('//div[@class="articleCon"]//a/text()').extract()
                        if accessory_pdfs:
                            accessory_pdf = []
                            for pdf in accessory_pdfs:
                                if 'http' not in pdf:
                                    pdf = self.base_url + pdf
                                accessory_pdf.append(pdf)
                            item['accessory_pdf'] = accessory_pdf
                            item['accessory_name'] = accessory_name
                        else:
                            item['accessory_pdf'] = []
                            item['accessory_name'] = []
                        content = response.xpath('//div[@class="article"]').extract_first()
                        if content:
                            content = content + '<br>' + item['content']
                            next_url = response.xpath('//div[@class="tPage"]/a[text()="下一页"]/@href').extract_first()
                            if next_url:
                                item['content'] = deal_content(content) if content else ''
                                return scrapy.Request(url=next_url, callback=self.parse_detail, meta={'item': item},
                                                      dont_filter=True)
                            else:
                                item['content'] = deal_content(content) if content else ''
                        else:
                            item['content'] = ''
                        yield item
        except Exception as e:
            print(e, response.url)


class KaoyanSixSpider(scrapy.Spider):
    name = 'kaoyan_six'
    allowed_domains = ['kaoyan.com']
    start_urls = ['http://www.kaoyan.com/beijing/']
    base_url = 'http://www.kaoyan.com'
    custom_settings = {
        'ITEM_PIPELINES': {
            'kaoyan.pipelines.KaoyanPipeline': 300,
            # 'spider.pipeline.pipelines.ImageToPdfPipeline': 120,
            # 'spider.pipeline.pipelines.ReportsMssqlPipeline': 130,
        },
        'DOWNLOAD_DELAY': 1
    }

    def parse(self, response):
        elems = response.xpath('//dl[@class="schoolListItem"]')[151:161]
        for elem in elems:
            school_name = elem.xpath('./dt/a/text()').extract_first()
            url = elem.xpath('./dd[@class="quickItem"]/a/@href').extract_first()
            meta = {'school_name': school_name if school_name else ''}
            if url:
                if 'http' not in url:
                    url = self.base_url + url
                yield scrapy.Request(url=url, callback=self.parse_tag_list, meta=meta, dont_filter=True)
            # break

    def parse_tag_list(self, response):
        elems = response.xpath('//ul[@class="subGuideList"]/li')
        del elems[7]
        for elem in elems:
            try:
                meta = response.meta
                tag_name = elem.xpath('./a/text()').extract_first()
                meta['tag_name'] = tag_name
                tag_url = elem.xpath('./a/@href').extract_first()
                if tag_url:
                    if 'http' not in tag_url:
                        tag_url = self.base_url + tag_url
                    yield scrapy.Request(url=tag_url, callback=self.parse_list, meta=meta, dont_filter=True)
            except Exception as e:
                print('获取标签地址错误', e)
                continue

    def parse_list(self, response):
        elems = response.xpath('//ul[@class="subList"]/li')
        for elem in elems:
            try:
                item = KaoyanItem()
                item['school_name'] = response.meta['school_name']
                item['tag_name'] = response.meta['tag_name']
                content_title = elem.xpath('./a/text()').extract_first()
                item['content_title'] = deal_title(content_title) if content_title else ''
                item['content'] = ''
                detail_url = elem.xpath('./a/@href').extract_first()
                if detail_url:
                    if 'http' not in detail_url:
                        detail_url = self.base_url + detail_url
                    yield scrapy.Request(url=detail_url, callback=self.parse_detail, meta={"item": item},
                                         dont_filter=True)
            except Exception as e:
                print('详情页地址不允许访问', e)
                continue
        meta = response.meta
        next_page_url = response.xpath('//div[@class="tPage"]/a[text()="下一页"]/@href').extract_first()
        if next_page_url:
            if 'http' not in next_page_url:
                next_page_url = self.base_url + next_page_url
            yield scrapy.Request(url=next_page_url, callback=self.parse_list, meta=meta, dont_filter=True)

    def parse_detail(self, response):
        try:
            if response.status != 200:
                print(response.url, '：无响应', response.status)
                return
            else:
                item = response.meta['item']
                pdate = response.xpath('//div[@class="articleInfo"]/span[1]/text()').extract_first()
                if pdate:
                    pdate = pdate.split(' ')[0]
                    year = int(pdate.split('-')[0])
                    if year < 2017:
                        print('2017年以后的')
                        return
                    else:
                        item['src'] = response.url
                        item['sid'] = gen_sid(response.url)
                        item['pdate'] = pdate
                        item['download_status'] = 0
                        accessory_pdfs = response.xpath('//div[@class="articleCon"]//a/@href').extract()
                        accessory_name = response.xpath('//div[@class="articleCon"]//a/text()').extract()
                        if accessory_pdfs:
                            accessory_pdf = []
                            for pdf in accessory_pdfs:
                                if 'http' not in pdf:
                                    pdf = self.base_url + pdf
                                accessory_pdf.append(pdf)
                            item['accessory_pdf'] = accessory_pdf
                            item['accessory_name'] = accessory_name
                        else:
                            item['accessory_pdf'] = []
                            item['accessory_name'] = []
                        content = response.xpath('//div[@class="article"]').extract_first()
                        if content:
                            content = content + '<br>' + item['content']
                            next_url = response.xpath('//div[@class="tPage"]/a[text()="下一页"]/@href').extract_first()
                            if next_url:
                                item['content'] = deal_content(content) if content else ''
                                return scrapy.Request(url=next_url, callback=self.parse_detail, meta={'item': item},
                                                      dont_filter=True)
                            else:
                                item['content'] = deal_content(content) if content else ''
                        else:
                            item['content'] = ''
                        yield item
        except Exception as e:
            print(e, response.url)


class KaoyanSevenSpider(scrapy.Spider):
    name = 'kaoyan_seven'
    allowed_domains = ['kaoyan.com']
    start_urls = ['http://www.kaoyan.com/beijing/']
    base_url = 'http://www.kaoyan.com'
    custom_settings = {
        'ITEM_PIPELINES': {
            'kaoyan.pipelines.KaoyanPipeline': 300,
            # 'spider.pipeline.pipelines.ImageToPdfPipeline': 120,
            # 'spider.pipeline.pipelines.ReportsMssqlPipeline': 130,
        },
        'DOWNLOAD_DELAY': 1
    }

    def parse(self, response):
        elems = response.xpath('//dl[@class="schoolListItem"]')[161:171]
        for elem in elems:
            school_name = elem.xpath('./dt/a/text()').extract_first()
            url = elem.xpath('./dd[@class="quickItem"]/a/@href').extract_first()
            meta = {'school_name': school_name if school_name else ''}
            if url:
                if 'http' not in url:
                    url = self.base_url + url
                yield scrapy.Request(url=url, callback=self.parse_tag_list, meta=meta, dont_filter=True)
            # break

    def parse_tag_list(self, response):
        elems = response.xpath('//ul[@class="subGuideList"]/li')
        del elems[7]
        for elem in elems:
            try:
                meta = response.meta
                tag_name = elem.xpath('./a/text()').extract_first()
                meta['tag_name'] = tag_name
                tag_url = elem.xpath('./a/@href').extract_first()
                if tag_url:
                    if 'http' not in tag_url:
                        tag_url = self.base_url + tag_url
                    yield scrapy.Request(url=tag_url, callback=self.parse_list, meta=meta, dont_filter=True)
            except Exception as e:
                print('获取标签地址错误', e)
                continue

    def parse_list(self, response):
        elems = response.xpath('//ul[@class="subList"]/li')
        for elem in elems:
            try:
                item = KaoyanItem()
                item['school_name'] = response.meta['school_name']
                item['tag_name'] = response.meta['tag_name']
                content_title = elem.xpath('./a/text()').extract_first()
                item['content_title'] = deal_title(content_title) if content_title else ''
                item['content'] = ''
                detail_url = elem.xpath('./a/@href').extract_first()
                if detail_url:
                    if 'http' not in detail_url:
                        detail_url = self.base_url + detail_url
                    yield scrapy.Request(url=detail_url, callback=self.parse_detail, meta={"item": item},
                                         dont_filter=True)
            except Exception as e:
                print('详情页地址不允许访问', e)
                continue
        meta = response.meta
        next_page_url = response.xpath('//div[@class="tPage"]/a[text()="下一页"]/@href').extract_first()
        if next_page_url:
            if 'http' not in next_page_url:
                next_page_url = self.base_url + next_page_url
            yield scrapy.Request(url=next_page_url, callback=self.parse_list, meta=meta, dont_filter=True)

    def parse_detail(self, response):
        try:
            if response.status != 200:
                print(response.url, '：无响应', response.status)
                return
            else:
                item = response.meta['item']
                pdate = response.xpath('//div[@class="articleInfo"]/span[1]/text()').extract_first()
                if pdate:
                    pdate = pdate.split(' ')[0]
                    year = int(pdate.split('-')[0])
                    if year < 2017:
                        print('2017年以后的')
                        return
                    else:
                        item['src'] = response.url
                        item['sid'] = gen_sid(response.url)
                        item['pdate'] = pdate
                        item['download_status'] = 0
                        accessory_pdfs = response.xpath('//div[@class="articleCon"]//a/@href').extract()
                        accessory_name = response.xpath('//div[@class="articleCon"]//a/text()').extract()
                        if accessory_pdfs:
                            accessory_pdf = []
                            for pdf in accessory_pdfs:
                                if 'http' not in pdf:
                                    pdf = self.base_url + pdf
                                accessory_pdf.append(pdf)
                            item['accessory_pdf'] = accessory_pdf
                            item['accessory_name'] = accessory_name
                        else:
                            item['accessory_pdf'] = []
                            item['accessory_name'] = []
                        content = response.xpath('//div[@class="article"]').extract_first()
                        if content:
                            content = content + '<br>' + item['content']
                            next_url = response.xpath('//div[@class="tPage"]/a[text()="下一页"]/@href').extract_first()
                            if next_url:
                                item['content'] = deal_content(content) if content else ''
                                return scrapy.Request(url=next_url, callback=self.parse_detail, meta={'item': item},
                                                      dont_filter=True)
                            else:
                                item['content'] = deal_content(content) if content else ''
                        else:
                            item['content'] = ''
                        yield item
        except Exception as e:
            print(e, response.url)


class KaoyanEightSpider(scrapy.Spider):
    name = 'kaoyan_eight'
    allowed_domains = ['kaoyan.com']
    start_urls = ['http://www.kaoyan.com/beijing/']
    base_url = 'http://www.kaoyan.com'
    custom_settings = {
        'ITEM_PIPELINES': {
            'kaoyan.pipelines.KaoyanPipeline': 300,
            # 'spider.pipeline.pipelines.ImageToPdfPipeline': 120,
            # 'spider.pipeline.pipelines.ReportsMssqlPipeline': 130,
        },
        'DOWNLOAD_DELAY': 1
    }

    def parse(self, response):
        elems = response.xpath('//dl[@class="schoolListItem"]')[171:181]
        for elem in elems:
            school_name = elem.xpath('./dt/a/text()').extract_first()
            url = elem.xpath('./dd[@class="quickItem"]/a/@href').extract_first()
            meta = {'school_name': school_name if school_name else ''}
            if url:
                if 'http' not in url:
                    url = self.base_url + url
                yield scrapy.Request(url=url, callback=self.parse_tag_list, meta=meta, dont_filter=True)
            # break

    def parse_tag_list(self, response):
        elems = response.xpath('//ul[@class="subGuideList"]/li')
        del elems[7]
        for elem in elems:
            try:
                meta = response.meta
                tag_name = elem.xpath('./a/text()').extract_first()
                meta['tag_name'] = tag_name
                tag_url = elem.xpath('./a/@href').extract_first()
                if tag_url:
                    if 'http' not in tag_url:
                        tag_url = self.base_url + tag_url
                    yield scrapy.Request(url=tag_url, callback=self.parse_list, meta=meta, dont_filter=True)
            except Exception as e:
                print('获取标签地址错误', e)
                continue

    def parse_list(self, response):
        elems = response.xpath('//ul[@class="subList"]/li')
        for elem in elems:
            try:
                item = KaoyanItem()
                item['school_name'] = response.meta['school_name']
                item['tag_name'] = response.meta['tag_name']
                content_title = elem.xpath('./a/text()').extract_first()
                item['content_title'] = deal_title(content_title) if content_title else ''
                item['content'] = ''
                detail_url = elem.xpath('./a/@href').extract_first()
                if detail_url:
                    if 'http' not in detail_url:
                        detail_url = self.base_url + detail_url
                    yield scrapy.Request(url=detail_url, callback=self.parse_detail, meta={"item": item},
                                         dont_filter=True)
            except Exception as e:
                print('详情页地址不允许访问', e)
                continue
        meta = response.meta
        next_page_url = response.xpath('//div[@class="tPage"]/a[text()="下一页"]/@href').extract_first()
        if next_page_url:
            if 'http' not in next_page_url:
                next_page_url = self.base_url + next_page_url
            yield scrapy.Request(url=next_page_url, callback=self.parse_list, meta=meta, dont_filter=True)

    def parse_detail(self, response):
        try:
            if response.status != 200:
                print(response.url, '：无响应', response.status)
                return
            else:
                item = response.meta['item']
                pdate = response.xpath('//div[@class="articleInfo"]/span[1]/text()').extract_first()
                if pdate:
                    pdate = pdate.split(' ')[0]
                    year = int(pdate.split('-')[0])
                    if year < 2017:
                        print('2017年以后的')
                        return
                    else:
                        item['src'] = response.url
                        item['sid'] = gen_sid(response.url)
                        item['pdate'] = pdate
                        item['download_status'] = 0
                        accessory_pdfs = response.xpath('//div[@class="articleCon"]//a/@href').extract()
                        accessory_name = response.xpath('//div[@class="articleCon"]//a/text()').extract()
                        if accessory_pdfs:
                            accessory_pdf = []
                            for pdf in accessory_pdfs:
                                if 'http' not in pdf:
                                    pdf = self.base_url + pdf
                                accessory_pdf.append(pdf)
                            item['accessory_pdf'] = accessory_pdf
                            item['accessory_name'] = accessory_name
                        else:
                            item['accessory_pdf'] = []
                            item['accessory_name'] = []
                        content = response.xpath('//div[@class="article"]').extract_first()
                        if content:
                            content = content + '<br>' + item['content']
                            next_url = response.xpath('//div[@class="tPage"]/a[text()="下一页"]/@href').extract_first()
                            if next_url:
                                item['content'] = deal_content(content) if content else ''
                                return scrapy.Request(url=next_url, callback=self.parse_detail, meta={'item': item},
                                                      dont_filter=True)
                            else:
                                item['content'] = deal_content(content) if content else ''
                        else:
                            item['content'] = ''
                        yield item
        except Exception as e:
            print(e, response.url)


class KaoyanNineSpider(scrapy.Spider):
    name = 'kaoyan_nine'
    allowed_domains = ['kaoyan.com']
    start_urls = ['http://www.kaoyan.com/beijing/']
    base_url = 'http://www.kaoyan.com'
    custom_settings = {
        'ITEM_PIPELINES': {
            'kaoyan.pipelines.KaoyanPipeline': 300,
            # 'spider.pipeline.pipelines.ImageToPdfPipeline': 120,
            # 'spider.pipeline.pipelines.ReportsMssqlPipeline': 130,
        },
        'DOWNLOAD_DELAY': 1
    }

    def parse(self, response):
        elems = response.xpath('//dl[@class="schoolListItem"]')[181:191]
        for elem in elems:
            school_name = elem.xpath('./dt/a/text()').extract_first()
            url = elem.xpath('./dd[@class="quickItem"]/a/@href').extract_first()
            meta = {'school_name': school_name if school_name else ''}
            if url:
                if 'http' not in url:
                    url = self.base_url + url
                yield scrapy.Request(url=url, callback=self.parse_tag_list, meta=meta, dont_filter=True)
            # break

    def parse_tag_list(self, response):
        elems = response.xpath('//ul[@class="subGuideList"]/li')
        del elems[7]
        for elem in elems:
            try:
                meta = response.meta
                tag_name = elem.xpath('./a/text()').extract_first()
                meta['tag_name'] = tag_name
                tag_url = elem.xpath('./a/@href').extract_first()
                if tag_url:
                    if 'http' not in tag_url:
                        tag_url = self.base_url + tag_url
                    yield scrapy.Request(url=tag_url, callback=self.parse_list, meta=meta, dont_filter=True)
            except Exception as e:
                print('获取标签地址错误', e)
                continue

    def parse_list(self, response):
        elems = response.xpath('//ul[@class="subList"]/li')
        for elem in elems:
            try:
                item = KaoyanItem()
                item['school_name'] = response.meta['school_name']
                item['tag_name'] = response.meta['tag_name']
                content_title = elem.xpath('./a/text()').extract_first()
                item['content_title'] = deal_title(content_title) if content_title else ''
                item['content'] = ''
                detail_url = elem.xpath('./a/@href').extract_first()
                if detail_url:
                    if 'http' not in detail_url:
                        detail_url = self.base_url + detail_url
                    yield scrapy.Request(url=detail_url, callback=self.parse_detail, meta={"item": item},
                                         dont_filter=True)
            except Exception as e:
                print('详情页地址不允许访问', e)
                continue
        meta = response.meta
        next_page_url = response.xpath('//div[@class="tPage"]/a[text()="下一页"]/@href').extract_first()
        if next_page_url:
            if 'http' not in next_page_url:
                next_page_url = self.base_url + next_page_url
            yield scrapy.Request(url=next_page_url, callback=self.parse_list, meta=meta, dont_filter=True)

    def parse_detail(self, response):
        try:
            if response.status != 200:
                print(response.url, '：无响应', response.status)
                return
            else:
                item = response.meta['item']
                pdate = response.xpath('//div[@class="articleInfo"]/span[1]/text()').extract_first()
                if pdate:
                    pdate = pdate.split(' ')[0]
                    year = int(pdate.split('-')[0])
                    if year < 2017:
                        print('2017年以后的')
                        return
                    else:
                        item['src'] = response.url
                        item['sid'] = gen_sid(response.url)
                        item['pdate'] = pdate
                        item['download_status'] = 0
                        accessory_pdfs = response.xpath('//div[@class="articleCon"]//a/@href').extract()
                        accessory_name = response.xpath('//div[@class="articleCon"]//a/text()').extract()
                        if accessory_pdfs:
                            accessory_pdf = []
                            for pdf in accessory_pdfs:
                                if 'http' not in pdf:
                                    pdf = self.base_url + pdf
                                accessory_pdf.append(pdf)
                            item['accessory_pdf'] = accessory_pdf
                            item['accessory_name'] = accessory_name
                        else:
                            item['accessory_pdf'] = []
                            item['accessory_name'] = []
                        content = response.xpath('//div[@class="article"]').extract_first()
                        if content:
                            content = content + '<br>' + item['content']
                            next_url = response.xpath('//div[@class="tPage"]/a[text()="下一页"]/@href').extract_first()
                            if next_url:
                                item['content'] = deal_content(content) if content else ''
                                return scrapy.Request(url=next_url, callback=self.parse_detail, meta={'item': item},
                                                      dont_filter=True)
                            else:
                                item['content'] = deal_content(content) if content else ''
                        else:
                            item['content'] = ''
                        yield item
        except Exception as e:
            print(e, response.url)


class KaoyanElevenSpider(scrapy.Spider):
    name = 'kaoyan_eleven'
    allowed_domains = ['kaoyan.com']
    start_urls = ['http://www.kaoyan.com/beijing/']
    base_url = 'http://www.kaoyan.com'
    custom_settings = {
        'ITEM_PIPELINES': {
            'kaoyan.pipelines.KaoyanPipeline': 300,
            # 'spider.pipeline.pipelines.ImageToPdfPipeline': 120,
            # 'spider.pipeline.pipelines.ReportsMssqlPipeline': 130,
        },
        'DOWNLOAD_DELAY': 1
    }

    def parse(self, response):
        elems = response.xpath('//dl[@class="schoolListItem"]')[191:201]
        for elem in elems:
            school_name = elem.xpath('./dt/a/text()').extract_first()
            url = elem.xpath('./dd[@class="quickItem"]/a/@href').extract_first()
            meta = {'school_name': school_name if school_name else ''}
            if url:
                if 'http' not in url:
                    url = self.base_url + url
                yield scrapy.Request(url=url, callback=self.parse_tag_list, meta=meta, dont_filter=True)
            # break

    def parse_tag_list(self, response):
        elems = response.xpath('//ul[@class="subGuideList"]/li')
        del elems[7]
        for elem in elems:
            try:
                meta = response.meta
                tag_name = elem.xpath('./a/text()').extract_first()
                meta['tag_name'] = tag_name
                tag_url = elem.xpath('./a/@href').extract_first()
                if tag_url:
                    if 'http' not in tag_url:
                        tag_url = self.base_url + tag_url
                    yield scrapy.Request(url=tag_url, callback=self.parse_list, meta=meta, dont_filter=True)
            except Exception as e:
                print('获取标签地址错误', e)
                continue

    def parse_list(self, response):
        elems = response.xpath('//ul[@class="subList"]/li')
        for elem in elems:
            try:
                item = KaoyanItem()
                item['school_name'] = response.meta['school_name']
                item['tag_name'] = response.meta['tag_name']
                content_title = elem.xpath('./a/text()').extract_first()
                item['content_title'] = deal_title(content_title) if content_title else ''
                item['content'] = ''
                detail_url = elem.xpath('./a/@href').extract_first()
                if detail_url:
                    if 'http' not in detail_url:
                        detail_url = self.base_url + detail_url
                    yield scrapy.Request(url=detail_url, callback=self.parse_detail, meta={"item": item},
                                         dont_filter=True)
            except Exception as e:
                print('详情页地址不允许访问', e)
                continue
        meta = response.meta
        next_page_url = response.xpath('//div[@class="tPage"]/a[text()="下一页"]/@href').extract_first()
        if next_page_url:
            if 'http' not in next_page_url:
                next_page_url = self.base_url + next_page_url
            yield scrapy.Request(url=next_page_url, callback=self.parse_list, meta=meta, dont_filter=True)

    def parse_detail(self, response):
        try:
            if response.status != 200:
                print(response.url, '：无响应', response.status)
                return
            else:
                item = response.meta['item']
                pdate = response.xpath('//div[@class="articleInfo"]/span[1]/text()').extract_first()
                if pdate:
                    pdate = pdate.split(' ')[0]
                    year = int(pdate.split('-')[0])
                    if year < 2017:
                        print('2017年以后的')
                        return
                    else:
                        item['src'] = response.url
                        item['sid'] = gen_sid(response.url)
                        item['pdate'] = pdate
                        item['download_status'] = 0
                        accessory_pdfs = response.xpath('//div[@class="articleCon"]//a/@href').extract()
                        accessory_name = response.xpath('//div[@class="articleCon"]//a/text()').extract()
                        if accessory_pdfs:
                            accessory_pdf = []
                            for pdf in accessory_pdfs:
                                if 'http' not in pdf:
                                    pdf = self.base_url + pdf
                                accessory_pdf.append(pdf)
                            item['accessory_pdf'] = accessory_pdf
                            item['accessory_name'] = accessory_name
                        else:
                            item['accessory_pdf'] = []
                            item['accessory_name'] = []
                        content = response.xpath('//div[@class="article"]').extract_first()
                        if content:
                            content = content + '<br>' + item['content']
                            next_url = response.xpath('//div[@class="tPage"]/a[text()="下一页"]/@href').extract_first()
                            if next_url:
                                item['content'] = deal_content(content) if content else ''
                                return scrapy.Request(url=next_url, callback=self.parse_detail, meta={'item': item},
                                                      dont_filter=True)
                            else:
                                item['content'] = deal_content(content) if content else ''
                        else:
                            item['content'] = ''
                        yield item
        except Exception as e:
            print(e, response.url)
