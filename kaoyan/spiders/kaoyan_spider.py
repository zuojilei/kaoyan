# -*- coding: utf-8 -*-
import scrapy,re
from kaoyan.items import KaoyanItem

class KaoyanSpiderSpider(scrapy.Spider):
    name = 'kaoyan_spider'
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
            tag_names = elem.xpath('./dd[@class="quickItem"]/a')
            for name in tag_names:
                tag_name = name.xpath('./text()').extract_first()
                meta = {
                    'school_name':school_name if school_name else '',
                    'tag_name': tag_name if tag_name else ''
                }
                tag_url = name.xpath('./@href').extract_first()
                if tag_url:
                    if 'http' not in tag_url:
                        tag_url = self.base_url + tag_url
                    yield scrapy.Request(url=tag_url, callback=self.parse_list, meta=meta, dont_filter=True)
                break
            break

    def parse_list(self, response):
        elems = response.xpath('//ul[@class="subList"]/li')
        meta = response.meta
        for elem in elems:
            meta = response.meta
            content_title = elem.xpath('./a/text()').extract_first()
            meta['content_title'] = content_title if content_title else ''
            meta['content'] = ''
            detail_url = elem.xpath('./a/@href').extract_first()
            if detail_url:
                if 'http' not in detail_url:
                    detail_url = self.base_url + detail_url
                yield scrapy.Request(url=detail_url, callback=self.parse_detail, meta=meta,dont_filter=True)

        next_page_url = response.xpath('//div[@class="tPage"]/a[text()="下一页"]/@href').extract_first()
        if next_page_url:
            if 'http' not in next_page_url:
                next_page_url = self.base_url + next_page_url
            yield scrapy.Request(url=next_page_url, callback=self.parse_list, meta=meta, dont_filter=True)

    def parse_detail(self, response):
        item = KaoyanItem()
        item['school_name'] = response.meta['school_name']
        item['tag_name'] = response.meta['tag_name']
        item['content_title'] = response.meta['content_title']
        item['content'] = response.meta['content']
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
            next_url = response.xpath('//div[@class="tPage"]/a[text()="下一页"]/@href')
            if next_url:
                item['content'] = self.deal_content(content) if content else ''
                yield scrapy.Request(url=next_url, callback=self.parse_detail, meta={'item':item}, dont_filter=True)
            else:
                item['content'] = self.deal_content(content) if content else ''
        else:
            item['content'] = ''
        yield item

    def deal_content(self, content):
        pattern1 = re.compile(r'<div class="qqShare".*?>.*?</div>',re.S)
        pattern2 = re.compile(r'<script type="text/javascript">.*?</script>',re.S)
        pattern3 = re.compile(r'<!-- qq分享.*?>',re.S)
        # pattern4 = re.compile(r'<a.*?>',re.S)
        # pattern5 = re.compile(r'</a>', re.S)

        content = pattern1.sub('', content)
        content = pattern2.sub('', content)
        content = pattern3.sub('', content)
        # content = pattern4.sub('<p>', content)
        # content = pattern5.sub('</p>', content)
        content = content.replace('\s', '')
        content = content.replace('\n', '')
        content = content.replace('\r', '')
        content = content.replace('\t', '')
        content = content.replace('\xa0', '')
        content = content.replace('\r\n', '')
        content = content.replace('&amp;', '')
        content = content.replace('\u3000', '')
        return content

    # def parse_content(self, content):
    #     """
    #     :param content: 去除、替换不符合的标签
    #     :return: 符合的content
    #     """
    #     elem1 = re.compile(r'<script.*?>.*?</script>', re.S)
    #     elem2 = re.compile(r'<section.*?>|</section>', re.S)
    #     elem3 = re.compile(r'<ins.*?>.*?</ins>', re.S)
    #     elem4 = re.compile(r'<h1.*?>|</h1>', re.S)
    #     elem5 = re.compile(r'<h2.*?>|</h2>', re.S)
    #     elem6 = re.compile(r'<h4.*?>|</h4>', re.S)
    #     elem7 = re.compile(r'<h3.*?>.*?</h3>', re.S)
    #     elem8 = re.compile(r'<embed.*?>', re.S)
    #     elem9 = re.compile(r'<span.*?>|</span>', re.S)
    #     elem10 = re.compile(r'<a.*?>|</a>', re.S)
    #     elem11 = re.compile(r'<span.*?>|</span>', re.S)
    #     elem12 = re.compile(r'<p.*?>', re.S)
    #     elem13 = re.compile(r'<ul.*?>', re.S)
    #     elem14 = re.compile(r'<li.*?>', re.S)
    #     elem15 = re.compile(r'<img.*?>|<p><img.*?>|<img.*?></p>|<p><strong><img.*?>|<img.*?></strong></p>', re.S)
    #     elem16 = re.compile(r'<br.*?>', re.S)
    #     elem17 = re.compile(r'<p></p>', re.S)
    #     elem18 = re.compile(r'<p><br></p>', re.S)
    #     elem19 = re.compile(r'<strong.*?>', re.S)
    #     elem20 = re.compile(r'<input.*?>', re.S)
    #     elem21 = re.compile(r'<blockquote.*?>|</blockquote>', re.S)
    #
    #     content = elem1.sub('', content)
    #     content = elem2.sub('', content)
    #     content = elem3.sub('', content)
    #     content = elem4.sub('', content)
    #     content = elem5.sub('', content)
    #     content = elem6.sub('', content)
    #     content = elem7.sub('', content)
    #     content = elem8.sub('', content)
    #     content = elem9.sub('', content)
    #     content = elem10.sub('', content)
    #     content = elem11.sub('', content)
    #     content = elem12.sub('<p>', content)
    #     content = elem13.sub('<ul>', content)
    #     content = elem14.sub('<li>', content)
    #     content = content.replace(' ', '')
    #     content = elem15.sub('<img src="%s">', content)
    #     content = elem16.sub('<br>', content)
    #     content = elem17.sub('', content)
    #     content = elem18.sub('', content)
    #     content = elem19.sub('<strong>', content)
    #     content = elem20.sub('', content)
    #     content = elem21.sub('', content)
    #
    #     content = content.replace('\s', '')
    #     content = content.replace('\n', '')
    #     content = content.replace('\r', '')
    #     content = content.replace('\t', '')
    #     content = content.replace('\xa0', '')
    #     content = content.replace('\r\n', '')
    #     content = content.replace('&amp;', '')
    #     content = content.replace('\u3000', '')
    #
    #     return content