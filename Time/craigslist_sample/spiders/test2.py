import scrapy
import re
import os.path
from lxml import etree
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from craigslist_sample.items import TimeItem
from scrapy.utils.response import body_or_str

class MySpider(CrawlSpider):
    name = "time"
    allowed_domains = ["time.com"]
    start_urls = ["http://time.com/"]

    base_url = 'http://content.time.com/time/static/sitemap/'
    year = ['1','2','3','4','5','6','7','8','9','10']
    month = ['12','11','10','9','8','7','6','5','4','3','2','1']
    page = ['12','11','10','9','8','7','6','5','4','3','2','1']

    def parse(self,response):
        for y in self.year:
            for m in self.month:
                 for p in self.page:
                    url = self.base_url+y+'_'+m+'_'+p+'.html'
                    yield scrapy.Request(url,self.parseList)

    def parseList(self, response):
        sel = Selector(response)
        articles = sel.xpath('//div[@class="listing"]/ul/li/a').extract()
        for article in articles:
            root = etree.fromstring(article)
            link = root.attrib['href']
            if link.startswith('http://content.time.com/'):
                continue
            yield scrapy.Request(link,self.parse_items)

    def parse_items(self, response):
        hxs = Selector(response)
        items = []
        item = TimeItem()
        item["title"] = hxs.xpath('//h1[contains(@class,"entry-title") or contains(@class, "article-tittle")]/text()').extract()[0]
        article = hxs.xpath('//div[contains(@class,"entry-content") or contains(@class,"article-content")]/p/text()').extract()
        item["article"] = "".join(article).encode('utf8')
        item['link'] = response.url
        pattern = re.compile(r"\d{4}-\d{2}-\d{2}",re.MULTILINE | re.DOTALL)
        item["date"] = hxs.xpath('//script[contains(.,"__reach_config = ") or contains(.,"utag_data =")]/text()').re(pattern)[0].encode('utf8')
        items.append(item)

        return items