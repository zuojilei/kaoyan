import os,time
import sys
from multiprocessing import Process
from scrapy import cmdline



# 配置参数即可, 爬虫名称，运行频率
confs = [
    'kaoyan_one',
    'kaoyan_two',
    'kaoyan_three',
    # 'kaoyan_four',
    # 'kaoyan_five',
    # 'kaoyan_six',
    'kaoyan_seven',
    # 'kaoyan_eight',
    # 'kaoyan_nine',
    # 'kaoyan_eleven'
]

def start_spider(spider_name):
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    args = ["scrapy", "crawl", spider_name]
    p = Process(target=cmdline.execute, args=(args,))
    p.start()
    p.join()


if __name__ == '__main__':
    for conf in confs:
        try:
            process = Process(target=start_spider, args=(conf,))
            process.start()
            time.sleep(2)
        except Exception:
            time.sleep(2)
            continue
